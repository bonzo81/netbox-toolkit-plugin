"""Netmiko-based device connector implementation."""
import time
from typing import Dict, Any, Optional, Tuple

from netmiko import ConnectHandler, SSHDetect
from netmiko.exceptions import (
    NetmikoTimeoutException, 
    NetmikoAuthenticationException,
    NetmikoBaseException,
    ConnectionException,
    ConfigInvalidException
)

from .base import BaseDeviceConnector, ConnectionConfig, CommandResult
from ..config import ToolkitConfig
from ..exceptions import DeviceConnectionError, CommandExecutionError, UnsupportedPlatformError
from ..utils.network import validate_device_connectivity
from ..utils.error_parser import VendorErrorParser
from ..utils.logging import get_toolkit_logger

logger = get_toolkit_logger(__name__)


class NetmikoConnector(BaseDeviceConnector):
    """Netmiko-based implementation of device connector for legacy/fallback support."""
    
    # NetBox platform to Netmiko device_type mapping
    DEVICE_TYPE_MAP = {
        'cisco_ios': 'cisco_ios',
        'cisco_nxos': 'cisco_nxos',
        'cisco_iosxr': 'cisco_xr',
        'cisco_xe': 'cisco_ios',
        'cisco_asa': 'cisco_asa',
        'arista_eos': 'arista_eos',
        'juniper_junos': 'juniper_junos',
        'hp_procurve': 'hp_procurve',
        'hp_comware': 'hp_comware',
        'dell_os10': 'dell_os10',
        'dell_powerconnect': 'dell_powerconnect',
        'linux': 'linux',
        'paloalto_panos': 'paloalto_panos',
        'fortinet': 'fortinet',
        'mikrotik_routeros': 'mikrotik_routeros',
        'ubiquiti_edge': 'ubiquiti_edge',
        # Generic fallback
        'generic': 'generic_termserver',
        'autodetect': 'autodetect'
    }
    
    def __init__(self, config: ConnectionConfig):
        super().__init__(config)
        self._error_parser = VendorErrorParser()
        self._retry_config = ToolkitConfig.get_retry_config()
        
        # Use config from extra_options if available, otherwise get from ToolkitConfig
        if config.extra_options:
            self._netmiko_config = config.extra_options.copy()
            logger.debug(f"Using Netmiko config from extra_options: {list(self._netmiko_config.keys())}")
        else:
            self._netmiko_config = ToolkitConfig.get_netmiko_config()
            logger.debug("Using default Netmiko config from ToolkitConfig")
        
        logger.debug(f"Initialized NetmikoConnector for {config.hostname} with platform '{config.platform}'")
    
    def _filter_valid_netmiko_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Filter parameters to only include those supported by Netmiko."""
        # Define valid Netmiko connection parameters
        valid_netmiko_params = {
            'device_type', 'host', 'username', 'password', 'port', 'timeout',
            'banner_timeout', 'auth_timeout', 'global_delay_factor', 'use_keys',
            'key_file', 'allow_agent', 'session_log', 'session_log_record_writes',
            'session_log_file_mode', 'fast_cli', 'secret', 'blocking_timeout',
            'verbose', 'conn_timeout', 'read_timeout', 'keepalive'
        }
        
        filtered_params = {}
        for key, value in params.items():
            if key in valid_netmiko_params:
                filtered_params[key] = value
            else:
                logger.debug(f"Filtering out unsupported Netmiko parameter: {key}")
        
        return filtered_params
    
    @classmethod
    def get_supported_platforms(cls) -> list:
        """Get list of supported platform names."""
        return list(cls.DEVICE_TYPE_MAP.keys())
    
    @classmethod
    def normalize_platform_name(cls, platform_name: str) -> str:
        """Normalize platform name for consistent mapping."""
        if not platform_name:
            return 'autodetect'
        
        normalized = platform_name.lower().strip()
        
        # Handle common variations
        platform_mappings = {
            'ios': 'cisco_ios',
            'nxos': 'cisco_nxos', 
            'nexus': 'cisco_nxos',
            'iosxr': 'cisco_iosxr',
            'ios-xr': 'cisco_iosxr',
            'ios-xe': 'cisco_xe',
            'eos': 'arista_eos',
            'junos': 'juniper_junos',
            'asa': 'cisco_asa',
        }
        
        return platform_mappings.get(normalized, normalized)
    
    def _get_device_type(self) -> str:
        """Get the appropriate Netmiko device_type for the platform."""
        if not self.config.platform:
            logger.debug("No platform specified, attempting auto-detection")
            return 'autodetect'
        
        normalized_platform = self.normalize_platform_name(self.config.platform)
        device_type = self.DEVICE_TYPE_MAP.get(normalized_platform, 'autodetect')
        
        logger.debug(f"Platform '{normalized_platform}' mapped to device_type '{device_type}'")
        return device_type
    
    def _auto_detect_device_type(self) -> str:
        """Use Netmiko's auto-detection for unknown platforms."""
        try:
            logger.debug(f"Attempting auto-detection for {self.config.hostname}")
            
            device_dict = {
                'device_type': 'autodetect',
                'host': self.config.hostname,
                'username': self.config.username,
                'password': self.config.password,
                'port': self.config.port,
                'timeout': self.config.timeout_socket,
            }
            
            guesser = SSHDetect(**device_dict)
            best_match = guesser.autodetect()
            
            if best_match:
                logger.info(f"Auto-detected device type '{best_match}' for {self.config.hostname}")
                return best_match
            else:
                logger.warning(f"Auto-detection failed for {self.config.hostname}, using generic")
                return 'generic_termserver'
                
        except Exception as e:
            logger.warning(f"Auto-detection error for {self.config.hostname}: {str(e)}")
            return 'generic_termserver'
    
    def _build_connection_params(self) -> Dict[str, Any]:
        """Build connection parameters for Netmiko."""
        device_type = self._get_device_type()
        
        # Handle auto-detection
        if device_type == 'autodetect':
            device_type = self._auto_detect_device_type()
        
        params = {
            'device_type': device_type,
            'host': self.config.hostname,
            'username': self.config.username,
            'password': self.config.password,
            'port': self.config.port,
            'timeout': self.config.timeout_socket,
            'banner_timeout': self._netmiko_config.get('banner_timeout', 15),
            'auth_timeout': self._netmiko_config.get('auth_timeout', 15),
            'blocking_timeout': self.config.timeout_ops,
        }
        
        # Add advanced options from Netmiko config
        if 'global_delay_factor' in self._netmiko_config:
            params['global_delay_factor'] = self._netmiko_config['global_delay_factor']
        
        if 'session_log' in self._netmiko_config and self._netmiko_config['session_log']:
            params['session_log'] = self._netmiko_config['session_log']
        
        # SSH key options - only set if explicitly enabled
        if self._netmiko_config.get('use_keys', False):
            params['use_keys'] = True
            if 'key_file' in self._netmiko_config:
                params['key_file'] = self._netmiko_config['key_file']
        else:
            # Explicitly disable key authentication for faster connections
            params['use_keys'] = False
            
        # SSH agent options
        if not self._netmiko_config.get('allow_agent', True):
            params['allow_agent'] = False
        
        # Add any other valid Netmiko options from extra_options
        if self.config.extra_options:
            # Filter to only include valid Netmiko parameters
            valid_params = self._filter_valid_netmiko_params(self.config.extra_options)
            params.update(valid_params)
        
        logger.debug(f"Netmiko connection params: device_type={device_type}, host={params['host']}")
        return params
    
    def connect(self) -> None:
        """Establish connection to the device using Netmiko with retry logic."""
        if self._connection:
            logger.debug(f"Already connected to {self.config.hostname}")
            return
        
        # Validate connectivity first
        validate_device_connectivity(self.config.hostname, self.config.port)
        
        max_retries = self._retry_config['max_retries']
        retry_delay = self._retry_config['retry_delay']
        last_error = None
        
        for attempt in range(max_retries + 1):
            try:
                if attempt > 0:
                    logger.debug(f"Connection attempt {attempt + 1}/{max_retries + 1} after {retry_delay}s delay")
                    time.sleep(retry_delay)
                    retry_delay *= self._retry_config['backoff_multiplier']
                else:
                    logger.debug(f"Initial connection attempt to {self.config.hostname}")
                
                # Build connection parameters
                conn_params = self._build_connection_params()
                
                # Create and establish connection
                logger.debug(f"Creating Netmiko ConnectHandler for {self.config.hostname}")
                self._connection = ConnectHandler(**conn_params)
                
                logger.info(f"Successfully connected to {self.config.hostname} using Netmiko")
                return
                
            except NetmikoAuthenticationException as e:
                logger.error(f"Authentication failed for {self.config.hostname}: {str(e)}")
                raise DeviceConnectionError(f"Authentication failed: {str(e)}")
            
            except NetmikoTimeoutException as e:
                last_error = e
                logger.warning(f"Connection timeout for {self.config.hostname}: {str(e)}")
                
                if attempt >= max_retries:
                    raise DeviceConnectionError(f"Connection timeout after {max_retries + 1} attempts: {str(e)}")
            
            except NetmikoBaseException as e:
                last_error = e
                logger.warning(f"Netmiko error for {self.config.hostname}: {str(e)}")
                
                if attempt >= max_retries:
                    raise DeviceConnectionError(f"Netmiko connection failed: {str(e)}")
            
            except Exception as e:
                last_error = e
                logger.warning(f"Unexpected error for {self.config.hostname}: {str(e)}")
                
                if attempt >= max_retries:
                    raise DeviceConnectionError(f"Connection failed: {str(e)}")
    
    def disconnect(self) -> None:
        """Close connection to the device."""
        if self._connection:
            logger.debug(f"Disconnecting from {self.config.hostname}")
            try:
                self._connection.disconnect()
                logger.debug("Successfully disconnected")
            except Exception as e:
                logger.warning(f"Error during disconnect: {str(e)}")
            finally:
                self._connection = None
    
    def execute_command(self, command: str, command_type: str = 'show') -> CommandResult:
        """Execute a command on the device.
        
        Args:
            command: The command string to execute
            command_type: Type of command ('show' or 'config') for proper handling
            
        Returns:
            CommandResult with execution details
        """
        if not self._connection:
            raise CommandExecutionError("Not connected to device")
        
        logger.debug(f"Executing {command_type} command on {self.config.hostname}: {command}")
        start_time = time.time()
        
        try:
            # Use command_type parameter to determine execution method
            if command_type == 'config':
                output = self._execute_config_command(command)
                parsed_data = None  # Config commands don't get parsed
            else:
                output, parsed_data = self._execute_show_command(command)
            
            execution_time = time.time() - start_time
            
            # Create initial result
            result = CommandResult(
                command=command,
                output=output,
                success=True,
                execution_time=execution_time
            )
            
            # Add parsed data if available
            if parsed_data:
                result.parsed_output = parsed_data
                result.parsing_success = True
                result.parsing_method = 'textfsm'
            
            # Check for syntax errors in the output even if command executed successfully
            parsed_error = self._error_parser.parse_command_output(output, self.config.platform)
            if parsed_error:
                logger.warning(f"Syntax error detected in command output: {parsed_error.error_type.value}")
                # Update result with syntax error information
                result.has_syntax_error = True
                result.syntax_error_type = parsed_error.error_type.value
                result.syntax_error_vendor = parsed_error.vendor
                result.syntax_error_guidance = parsed_error.guidance
                
                # Enhance the output with error information
                enhanced_output = output + "\n\n" + "="*50 + "\n"
                enhanced_output += "SYNTAX ERROR DETECTED\n" + "="*50 + "\n"
                enhanced_output += f"Error Type: {parsed_error.error_type.value.replace('_', ' ').title()}\n"
                enhanced_output += f"Vendor: {self._error_parser._get_vendor_display_name(parsed_error.vendor)}\n"
                enhanced_output += f"Confidence: {parsed_error.confidence:.0%}\n\n"
                enhanced_output += parsed_error.enhanced_message + "\n\n"
                enhanced_output += parsed_error.guidance
                
                result.output = enhanced_output
            
            # Log final result summary
            if parsed_data:
                logger.debug(f"Command completed in {execution_time:.2f}s with {len(parsed_data)} parsed records")
            else:
                logger.debug(f"Command completed in {execution_time:.2f}s")
            return result
            
        except NetmikoBaseException as e:
            execution_time = time.time() - start_time
            error_msg = str(e)
            logger.error(f"Command execution failed: {error_msg}")
            
            return CommandResult(
                command=command,
                output="",
                success=False,
                error_message=error_msg,
                execution_time=execution_time
            )
        
        except Exception as e:
            execution_time = time.time() - start_time
            error_msg = f"Unexpected error: {str(e)}"
            logger.error(f"Command execution failed: {error_msg}")
            
            return CommandResult(
                command=command,
                output="",
                success=False,
                error_message=error_msg,
                execution_time=execution_time
            )
    
    def _execute_show_command(self, command: str) -> Tuple[str, Optional[list]]:
        """Execute a show/display command and return both raw output and parsed data.
        
        Args:
            command: The command to execute
            
        Returns:
            tuple: (raw_output, parsed_data) where parsed_data is None if parsing failed
        """
        try:
            # Execute command once and get raw output
            raw_output = self._connection.send_command(command)
            
            # Now attempt TextFSM parsing using the textfsm library directly
            # This avoids re-executing the command on the device
            parsed_data = None
            try:
                # Import textfsm here to avoid dependency issues if not installed
                import textfsm
                import os
                from ntc_templates.parse import parse_output
                
                # Try to parse using ntc-templates (which is what Netmiko uses)
                try:
                    parsed_result = parse_output(
                        platform=self._connection.device_type,
                        command=command,
                        data=raw_output
                    )
                    
                    if (isinstance(parsed_result, list) and 
                        len(parsed_result) > 0 and
                        isinstance(parsed_result[0], dict)):
                        parsed_data = parsed_result
                        logger.debug(f"TextFSM parsed {len(parsed_data)} records")
                    else:
                        logger.debug("No TextFSM template found")
                        
                except Exception as ntc_error:
                    logger.debug(f"TextFSM parsing failed: {str(ntc_error)}")
                        
            except ImportError:
                logger.debug("TextFSM or ntc-templates not available, skipping parsing")
            except Exception as parse_error:
                logger.debug(f"TextFSM parsing failed: {str(parse_error)}")
            
            return raw_output, parsed_data
            
        except Exception as e:
            logger.error(f"Show command failed: {str(e)}")
            raise CommandExecutionError(f"Show command failed: {str(e)}")
    
    def _execute_config_command(self, command: str) -> str:
        """Execute a configuration command."""
        try:
            if isinstance(command, str):
                commands = [command]
            else:
                commands = command
            
            return self._connection.send_config_set(commands)
        except Exception as e:
            logger.error(f"Config command failed: {str(e)}")
            raise CommandExecutionError(f"Config command failed: {str(e)}")
    
    # Note: The _attempt_parsing method has been removed as parsing is now handled
    # directly in _execute_show_command to avoid re-executing commands on the device
    
    def is_connected(self) -> bool:
        """Check if device is connected."""
        if not self._connection:
            return False
        
        try:
            # Simple connectivity test
            self._connection.find_prompt()
            return True
        except Exception:
            return False
