"""Scrapli-based device connector implementation."""
import time
from typing import Dict, Any, Type, Optional

from scrapli.driver.core import IOSXEDriver, NXOSDriver, IOSXRDriver
from scrapli.driver.generic import GenericDriver
from scrapli.exceptions import ScrapliException

from .base import BaseDeviceConnector, ConnectionConfig, CommandResult
from ..config import ToolkitConfig
from ..exceptions import DeviceConnectionError, CommandExecutionError, UnsupportedPlatformError
from ..utils.network import validate_device_connectivity
from ..utils.connection import cleanup_connection_resources, validate_connection_health, wait_for_socket_cleanup
from ..utils.error_parser import VendorErrorParser
from ..utils.logging import get_toolkit_logger

logger = get_toolkit_logger(__name__)


class ScrapliConnector(BaseDeviceConnector):
    """Scrapli-based implementation of device connector."""
    
    # Platform to driver mapping - expanded for better NetBox platform support
    DRIVER_MAP = {
        'cisco_ios': IOSXEDriver,
        'cisco_nxos': NXOSDriver,
        'cisco_iosxr': IOSXRDriver,
        'cisco_xe': IOSXEDriver,  # Alternative naming
        'ios': IOSXEDriver,       # Generic iOS
        'nxos': NXOSDriver,       # Shorter form
        'iosxr': IOSXRDriver,     # Shorter form
        'ios-xe': IOSXEDriver,    # Hyphenated form
        'ios-xr': IOSXRDriver,    # Hyphenated form
    }
    
    def __init__(self, config: ConnectionConfig):
        super().__init__(config)
        self._driver_class = self._get_driver_class()
        self._retry_config = ToolkitConfig.get_retry_config()
        self._error_parser = VendorErrorParser()
        self._fast_fail_mode = False  # Flag for using reduced timeouts on initial attempts
        
        logger.debug(f"Initialized ScrapliConnector for {config.hostname} with platform '{config.platform}'")
    
    @classmethod
    def get_supported_platforms(cls) -> list:
        """Get list of supported platform names."""
        return list(cls.DRIVER_MAP.keys()) + ['generic']
    
    @classmethod
    def normalize_platform_name(cls, platform_name: str) -> str:
        """Normalize platform name for consistent mapping."""
        if not platform_name:
            return 'generic'
        
        normalized = platform_name.lower().strip()
        
        # Handle common variations
        if normalized in ['cisco ios', 'ios', 'cisco_ios']:
            return 'cisco_ios'
        elif normalized in ['cisco nxos', 'nxos', 'nexus']:
            return 'cisco_nxos'
        elif normalized in ['cisco iosxr', 'iosxr', 'ios-xr']:
            return 'cisco_iosxr'
        elif normalized in ['cisco xe', 'ios-xe']:
            return 'cisco_xe'
        
        return normalized
    
    def _get_driver_class(self) -> Type:
        """Get the appropriate Scrapli driver class for the platform."""
        if not self.config.platform:
            logger.debug("No platform specified, using GenericDriver")
            return GenericDriver
        
        normalized_platform = self.normalize_platform_name(self.config.platform)
        driver_class = self.DRIVER_MAP.get(normalized_platform, GenericDriver)
        
        if driver_class == GenericDriver:
            logger.debug(f"Platform '{normalized_platform}' not in driver map, using GenericDriver")
        else:
            logger.debug(f"Platform '{normalized_platform}' mapped to {driver_class.__name__}")
            
        return driver_class
    
    def _build_connection_params(self) -> Dict[str, Any]:
        """Build connection parameters for Scrapli."""
        # Use fast test timeouts for initial attempts if in fast fail mode
        if self._fast_fail_mode:
            fast_timeouts = ToolkitConfig.get_fast_test_timeouts()
            socket_timeout = fast_timeouts['socket']
            transport_timeout = fast_timeouts['transport']
            ops_timeout = fast_timeouts['ops']
            logger.debug("Using fast test timeouts for initial connection attempt")
        else:
            socket_timeout = self.config.timeout_socket
            transport_timeout = self.config.timeout_transport
            ops_timeout = self.config.timeout_ops
        
        params = {
            'host': self.config.hostname,
            'auth_username': self.config.username,
            'auth_password': self.config.password,
            'auth_strict_key': self.config.auth_strict_key,
            'transport': self.config.transport,
            'timeout_socket': socket_timeout,
            'timeout_transport': transport_timeout,
            'timeout_ops': ops_timeout,
            'transport_options': self._get_transport_options()
        }
        
        # Add any extra options (but filter out Netmiko-specific ones)
        if self.config.extra_options:
            # Filter out Netmiko-specific parameters that Scrapli doesn't understand
            netmiko_only_params = {
                'look_for_keys', 'use_keys', 'allow_agent', 'global_delay_factor',
                'banner_timeout', 'auth_timeout', 'session_log', 'fast_cli',
                'session_log_record_writes', 'session_log_file_mode', 'conn_timeout',
                'read_timeout_override', 'auto_connect'
            }
            
            filtered_options = {
                k: v for k, v in self.config.extra_options.items() 
                if k not in netmiko_only_params
            }
            
            if filtered_options:
                params.update(filtered_options)
                logger.debug(f"Added filtered extra options: {list(filtered_options.keys())}")
            
            if len(filtered_options) != len(self.config.extra_options):
                excluded = set(self.config.extra_options.keys()) - set(filtered_options.keys())
                logger.debug(f"Excluded Netmiko-specific options: {excluded}")
        
        logger.debug(f"Built connection params for {self.config.hostname}: transport={params['transport']}, "
                    f"timeouts=[socket:{params['timeout_socket']}, transport:{params['timeout_transport']}, "
                    f"ops:{params['timeout_ops']}]")
        
        return params
    
    def _get_transport_options(self) -> Dict[str, Any]:
        """Get transport-specific options for Scrapli."""
        ssh_options = ToolkitConfig.get_ssh_transport_options()
        
        transport_options = {}
        
        # Add system transport options (Scrapli's native transport)
        if self.config.transport == 'system':
            transport_options['system'] = {
                'open_cmd': ['ssh'],
                'auth_bypass': False,
            }
        
        # Add SSH algorithm configurations
        if 'disabled_algorithms' in ssh_options:
            transport_options['disabled_algorithms'] = ssh_options['disabled_algorithms']
        
        if 'allowed_kex' in ssh_options:
            transport_options['kex_algorithms'] = ssh_options['allowed_kex']
        
        logger.debug(f"Transport options for {self.config.transport}: {transport_options}")
        return transport_options
    
    def connect(self) -> None:
        """Establish connection to the device with retry logic and fast-fail detection."""
        logger.debug(f"Attempting to connect to {self.config.hostname}:{self.config.port}")
        
        # Clean up any existing connection first
        if self._connection:
            logger.debug("Cleaning up existing connection before reconnecting")
            self.disconnect()
        
        # First validate basic connectivity
        try:
            logger.debug(f"Validating basic connectivity to {self.config.hostname}:{self.config.port}")
            validate_device_connectivity(self.config.hostname, self.config.port)
        except Exception as e:
            logger.error(f"Pre-connection validation failed for {self.config.hostname}: {str(e)}")
            raise DeviceConnectionError(f"Pre-connection validation failed: {str(e)}")
        
        # Use fast-fail mode for first attempt to quickly detect incompatible scenarios
        self._fast_fail_mode = True
        conn_params = self._build_connection_params()
        
        # Attempt connection with retry logic
        last_error = None
        retry_delay = self._retry_config['retry_delay']
        max_retries = self._retry_config['max_retries']
        
        logger.debug(f"Starting connection attempts with max_retries={max_retries}, initial_delay={retry_delay}s")
        
        for attempt in range(max_retries + 1):
            try:
                if attempt > 0:
                    logger.debug(f"Connection attempt {attempt + 1}/{max_retries + 1} after {retry_delay}s delay")
                    time.sleep(retry_delay)
                    
                    # Switch to normal timeouts after first attempt
                    if attempt == 1:
                        self._fast_fail_mode = False
                        conn_params = self._build_connection_params()
                        logger.debug("Switched to normal timeouts for subsequent attempts")
                    
                    # Adjust timeouts for SSH banner issues
                    if "banner" in str(last_error).lower() or "timed out" in str(last_error).lower():
                        logger.debug("Detected banner/timeout issue, increasing timeouts by 5s")
                        conn_params['timeout_socket'] += 5
                        conn_params['timeout_transport'] += 5
                    
                    retry_delay *= self._retry_config['backoff_multiplier']
                else:
                    logger.debug(f"Initial connection attempt to {self.config.hostname} (fast-fail mode)")
                
                # Create and open connection
                logger.debug(f"Creating {self._driver_class.__name__} instance")
                self._connection = self._driver_class(**conn_params)
                
                logger.debug("Opening connection to device")
                self._connection.open()
                
                logger.info(f"Successfully connected to {self.config.hostname} using {self._driver_class.__name__}")
                return
                
            except Exception as e:
                last_error = e
                error_msg = str(e)
                logger.warning(f"Connection attempt {attempt + 1} failed for {self.config.hostname}: {error_msg}")
                
                # Check for fast-fail patterns on first attempt
                if attempt == 0 and ToolkitConfig.should_fast_fail_to_netmiko(error_msg):
                    logger.info(f"Fast-fail pattern detected: {error_msg}")
                    logger.info("Triggering immediate fallback to Netmiko")
                    raise DeviceConnectionError(f"Fast-fail to Netmiko: {error_msg}")
                
                # Clean up failed connection attempt
                if self._connection:
                    try:
                        logger.debug("Cleaning up failed connection attempt")
                        self._connection.close()
                    except Exception:
                        pass
                    self._connection = None
                
                if attempt >= max_retries:
                    error_msg = self._format_connection_error(e)
                    logger.error(f"All connection attempts failed for {self.config.hostname}: {error_msg}")
                    raise DeviceConnectionError(error_msg)
    
    def disconnect(self) -> None:
        """Close connection to the device with proper socket cleanup."""
        if self._connection:
            logger.debug(f"Disconnecting from {self.config.hostname}")
            try:
                # Use the robust cleanup utility
                cleanup_connection_resources(self._connection)
                logger.debug("Connection cleanup completed successfully")
            except Exception as e:
                logger.warning(f"Error during connection cleanup: {str(e)}")
                pass  # Cleanup error ignored
            finally:
                self._connection = None
                # Give time for socket cleanup to complete
                wait_for_socket_cleanup()
                logger.debug("Socket cleanup wait completed")
        else:
            logger.debug("No active connection to disconnect")
    
    def is_connected(self) -> bool:
        """Check if connection is active with proper error handling."""
        if not self._connection:
            logger.debug("No connection object exists")
            return False
        
        try:
            # Check if connection object exists and is alive
            is_alive = self._connection.isalive()
            logger.debug(f"Connection status check: {'alive' if is_alive else 'dead'}")
            return is_alive
        except Exception as e:
            # If checking connection status fails, assume disconnected
            logger.warning(f"Error checking connection status: {str(e)}")
            # Clean up the bad connection
            self._connection = None
            return False
    
    def _validate_and_recover_connection(self) -> bool:
        """Validate connection and attempt recovery if needed."""
        try:
            if not self._connection:
                logger.debug("No connection to validate")
                return False
            
            # Use the robust validation utility
            is_healthy = validate_connection_health(self._connection)
            logger.debug(f"Connection health validation: {'healthy' if is_healthy else 'unhealthy'}")
            return is_healthy
            
        except Exception as e:
            logger.warning(f"Connection validation failed: {str(e)}")
            self._connection = None
            return False

    def execute_command(self, command: str, command_type: str = 'show') -> CommandResult:
        """Execute a command on the device with robust error handling.
        
        Args:
            command: The command string to execute
            command_type: Type of command ('show' or 'config') for proper scrapli method selection
            
        Returns:
            CommandResult with execution details
        """
        logger.debug(f"Executing {command_type} command on {self.config.hostname}: {command}")
        
        # Validate connection first
        if not self._validate_and_recover_connection():
            logger.error(f"Connection validation failed before executing command: {command}")
            raise DeviceConnectionError("Connection is not available or has been lost")
        
        start_time = time.time()
        
        try:
            # Use appropriate scrapli method based on command type
            if command_type == 'config':
                logger.debug("Using send_config method for configuration command")
                # Use send_config for configuration commands - automatically handles config mode
                response = self._connection.send_config(command)
            else:
                logger.debug("Using send_command method for show/operational command")
                # Use send_command for show/operational commands
                response = self._connection.send_command(command)
            
            execution_time = time.time() - start_time
            logger.debug(f"Command completed in {execution_time:.2f}s, output length: {len(response.result)} chars")
            
            # Create initial result
            result = CommandResult(
                command=command,
                output=response.result,
                success=True,
                execution_time=execution_time
            )
            
            # Check for syntax errors in the output even if command executed successfully
            parsed_error = self._error_parser.parse_command_output(response.result, self.config.platform)
            if parsed_error:
                logger.warning(f"Syntax error detected in command output: {parsed_error.error_type.value}")
                # Update result with syntax error information
                result.has_syntax_error = True
                result.syntax_error_type = parsed_error.error_type.value
                result.syntax_error_vendor = parsed_error.vendor
                result.syntax_error_guidance = parsed_error.guidance
                
                # Enhance the output with error information
                enhanced_output = response.result + "\n\n" + "="*50 + "\n"
                enhanced_output += "SYNTAX ERROR DETECTED\n" + "="*50 + "\n"
                enhanced_output += f"Error Type: {parsed_error.error_type.value.replace('_', ' ').title()}\n"
                enhanced_output += f"Vendor: {self._error_parser._get_vendor_display_name(parsed_error.vendor)}\n"
                enhanced_output += f"Confidence: {parsed_error.confidence:.0%}\n\n"
                enhanced_output += parsed_error.enhanced_message + "\n\n"
                enhanced_output += parsed_error.guidance
                
                result.output = enhanced_output
            
            # Attempt to parse command output using TextFSM (only for successful commands without syntax errors)
            if result.success and not result.has_syntax_error:
                logger.debug("Attempting to parse command output with TextFSM")
                result = self._attempt_parsing(result, response)
            
            return result
            
        except OSError as e:
            # Handle socket-related errors specifically
            execution_time = time.time() - start_time
            if "Bad file descriptor" in str(e) or e.errno == 9:
                # Socket has been closed or is invalid
                logger.error(f"Socket error during command execution: {str(e)}")
                self._connection = None  # Mark connection as invalid
                error_msg = f"Connection lost due to socket error: {str(e)}"
            else:
                logger.error(f"OS error during command execution: {str(e)}")
                error_msg = f"OS error during command execution: {str(e)}"
            
            return CommandResult(
                command=command,
                output="",
                success=False,
                error_message=error_msg,
                execution_time=execution_time
            )
        
        except Exception as e:
            execution_time = time.time() - start_time
            error_msg = f"Command execution failed: {str(e)}"
            logger.error(f"Command execution failed for '{command}': {str(e)}")
            
            # Check if this is a connection-related error
            if "connection" in str(e).lower() or "socket" in str(e).lower():
                logger.warning("Detected connection-related error, marking connection as invalid")
                self._connection = None  # Mark connection as invalid
            
            return CommandResult(
                command=command,
                output="",
                success=False,
                error_message=error_msg,
                execution_time=execution_time
            )

    def _attempt_parsing(self, result: CommandResult, response) -> CommandResult:
        """Attempt to parse command output using available parsers.
        
        Args:
            result: The current CommandResult
            response: The scrapli response object
            
        Returns:
            Updated CommandResult with parsing information
        """
        # Try TextFSM parsing first (most comprehensive template library)
        try:
            parsed_data = response.textfsm_parse_output()
            
            if parsed_data:
                # TextFSM parsing successful
                logger.debug(f"TextFSM parsing successful, parsed {len(parsed_data)} records")
                result.parsed_output = parsed_data
                result.parsing_success = True
                result.parsing_method = 'textfsm'
                
                return result
            else:
                logger.debug("TextFSM parsing returned empty result (no matching template)")
                pass  # TextFSM parsing returned empty result
                
        except Exception as e:
            # TextFSM parsing failed - this is common for commands without templates
            error_msg = str(e)
            logger.debug(f"TextFSM parsing failed: {error_msg}")
            
            # Store parsing error for debugging (but don't fail the command)
            result.parsing_error = f"TextFSM: {error_msg}"
        
        # Could add other parsers here in the future (Genie, TTP)
        # For now, we only attempt TextFSM
        
        return result

    def _format_connection_error(self, error: Exception) -> str:
        """Format connection error with helpful troubleshooting information."""
        error_message = str(error)
        
        # Base error message
        formatted_msg = f"Failed to connect to {self.config.hostname}: {error_message}"
        
        # Add specific guidance for common SSH errors
        if "No matching key exchange" in error_message:
            formatted_msg += (
                "\n\nThis appears to be an SSH key exchange error. The device is offering "
                "encryption algorithms that are not supported by default."
            )
        elif "connection not opened" in error_message:
            formatted_msg += (
                "\n\nUnable to establish SSH connection. This could be due to:"
                "\n- The device is not reachable on the network"
                "\n- SSH service is not running on the device"
                "\n- There's a firewall blocking the connection"
                "\n- The device has reached its maximum number of SSH sessions"
            )
        elif "Error reading SSH protocol banner" in error_message:
            formatted_msg += (
                "\n\nCould not read the SSH protocol banner from the device. This typically happens when:"
                "\n- The device accepts TCP connections on port 22 but is not running SSH"
                "\n- The device's SSH server is too slow to respond with a banner (timeout)"
                "\n- A firewall or security device is intercepting the connection"
                "\n- The SSH implementation on the device is non-standard or very old"
            )
        elif "Authentication failed" in error_message:
            formatted_msg += (
                "\n\nAuthentication failed. Please verify:"
                "\n- Username and password are correct"
                "\n- The account is not locked"
                "\n- The device allows the authentication method being used"
            )
        
        return formatted_msg
