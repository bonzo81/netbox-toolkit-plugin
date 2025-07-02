"""Service for handling command execution on devices."""
import traceback
from typing import Optional, Any

from dcim.models import Device

from ..models import Command, CommandLog
from ..connectors.factory import ConnectorFactory
from ..connectors.base import CommandResult
from ..connectors.netmiko_connector import NetmikoConnector
from ..exceptions import DeviceConnectionError, CommandExecutionError
from ..config import ToolkitConfig
from ..utils.logging import get_toolkit_logger

logger = get_toolkit_logger(__name__)


class CommandExecutionService:
    """Service for executing commands on devices."""
    
    def __init__(self):
        self.connector_factory = ConnectorFactory()
    
    def execute_command_with_retry(
        self,
        command: "PredefinedCommand",
        device: Any,
        username: str,
        password: str,
        max_retries: int = 1
    ) -> "CommandResult":
        """
        Execute a command with connection retry capability.
        
        Args:
            command: Command to execute
            device: Target device
            username: Authentication username
            password: Authentication password
            max_retries: Maximum number of retry attempts
            
        Returns:
            CommandResult with execution details
        """
        last_error = None
        
        logger.info("Executing command '%s' on device %s (max_retries=%d)", 
                   command.name, device.name, max_retries)
        
        for attempt in range(max_retries + 1):
            try:
                logger.debug("Attempt %d/%d for command execution", attempt + 1, max_retries + 1)
                
                # Create appropriate connector for the device
                connector = self.connector_factory.create_connector(device, username, password)
                logger.debug("Created %s connector for device %s", 
                           type(connector).__name__, device.name)
                
                # Execute command using context manager for proper cleanup
                with connector:
                    result = connector.execute_command(command.command, command.command_type)
                    logger.debug("Command executed successfully, output length: %d chars", 
                               len(result.output) if result.output else 0)
                
                # If successful, log and return
                logger.info("Command execution completed successfully on %s", device.name)
                self._log_command_execution(command, device, result, username)
                return result
                
            except Exception as e:
                last_error = e
                error_msg = str(e)
                logger.warning("Command execution attempt %d failed: %s", attempt + 1, error_msg)
                
                # Check for fast-fail scenario and automatically retry with Netmiko
                if ("Fast-fail to Netmiko" in error_msg or 
                    ToolkitConfig.should_fast_fail_to_netmiko(error_msg)):
                    logger.info("Fast-fail pattern detected, attempting fallback to Netmiko for device %s", device.name)
                    try:
                        # Create Netmiko connector directly for fallback
                        base_config = self.connector_factory._build_connection_config(device, username, password)
                        netmiko_config = self.connector_factory._prepare_connector_config(base_config, NetmikoConnector)
                        fallback_connector = NetmikoConnector(netmiko_config)
                        
                        # Execute command using Netmiko fallback connector
                        with fallback_connector:
                            result = fallback_connector.execute_command(command.command, command.command_type)
                            logger.info("Command executed successfully using Netmiko fallback on %s", device.name)
                            self._log_command_execution(command, device, result, username)
                            return result
                            
                    except Exception as fallback_error:
                        logger.warning("Netmiko fallback also failed for device %s: %s", device.name, str(fallback_error))
                        last_error = fallback_error
                        break  # Don't retry after fallback failure
                
                # If this was a socket/connection error and we have retries left, continue
                elif (attempt < max_retries and 
                      ("socket" in error_msg.lower() or 
                       "connection" in error_msg.lower() or 
                       "Bad file descriptor" in error_msg)):
                    logger.debug("Connection error detected, will retry")
                    continue
                else:
                    logger.error("Max retries reached or non-retryable error")
                    break
        
        # All attempts failed, create error result
        logger.error("All command execution attempts failed for device %s", device.name)
        error_result = CommandResult(
            command=command.command,
            output="",
            success=False,
            error_message=str(last_error)
        )
        
        # Add detailed error information
        error_result = self._enhance_error_result(error_result, last_error, device)
        
        # Log the failed execution
        self._log_command_execution(command, device, error_result, username)
        
        return error_result

    def execute_command(
        self,
        command: Command,
        device: Device,
        username: str,
        password: str
    ) -> CommandResult:
        """
        Execute a command on a device and log the result.
        
        Args:
            command: Command to execute
            device: Target device
            username: Authentication username
            password: Authentication password
            
        Returns:
            CommandResult with execution details
        """
        try:
            # Create appropriate connector for the device
            connector = self.connector_factory.create_connector(device, username, password)
            
            # Execute command using context manager for proper cleanup
            with connector:
                result = connector.execute_command(command.command, command.command_type)
            
            # Log the execution
            self._log_command_execution(command, device, result, username)
            
            return result
            
        except Exception as e:
            # Create error result
            error_result = CommandResult(
                command=command.command,
                output="",
                success=False,
                error_message=str(e)
            )
            
            # Add detailed error information
            error_result = self._enhance_error_result(error_result, e, device)
            
            # Log the failed execution
            self._log_command_execution(command, device, error_result, username)
            
            return error_result
    
    def _log_command_execution(
        self,
        command: Command,
        device: Device,
        result: CommandResult,
        username: str
    ) -> CommandLog:
        """Log command execution to database."""
        if result.success:
            output = result.output
            # If syntax error was detected, note it in the success flag
            if result.has_syntax_error:
                success = False  # Mark as failed due to syntax error
                error_message = f"Syntax error detected: {result.syntax_error_type}"
            else:
                success = True
                error_message = ""
        else:
            output = f"Error executing command: {result.error_message}"
            if result.output:
                output += f"\n\nOutput: {result.output}"
            success = False
            error_message = result.error_message or ''
        
        # Create log entry with execution details
        command_log = CommandLog.objects.create(
            command=command,
            device=device,
            output=output,
            username=username,
            success=success,
            error_message=error_message,
            execution_duration=result.execution_time,
            parsed_data=result.parsed_output,
            parsing_success=result.parsing_success,
            parsing_template=result.parsing_method
        )
        
        if result.has_syntax_error:
            pass  # Syntax error detected but not logging
        else:
            pass  # Command executed successfully but not logging
        
        return command_log
    
    def _enhance_error_result(self, result: CommandResult, error: Exception, device: Device) -> CommandResult:
        """Enhance error result with detailed troubleshooting information."""
        error_message = str(error)
        error_details = traceback.format_exc()
        
        enhanced_output = f"Error executing command: {error_message}"
        
        # Add specific guidance for common errors
        guidance_added = False
        
        if isinstance(error, DeviceConnectionError):
            enhanced_output += self._get_connection_error_guidance(error_message, device)
            guidance_added = True
        elif "Bad file descriptor" in error_details:
            enhanced_output += self._get_bad_descriptor_guidance(device)
            guidance_added = True
        elif "Error reading SSH protocol banner" in error_details:
            enhanced_output += self._get_banner_error_guidance(device)
            guidance_added = True
        
        # Check for connection/authentication errors in the error message even if not DeviceConnectionError
        if not guidance_added:
            error_lower = error_message.lower()
            if any(error_term in error_lower for error_term in [
                "connect", "connection", "authentication", "failed to connect", 
                "ssh", "timeout", "unreachable", "refused"
            ]):
                enhanced_output += self._get_connection_error_guidance(error_message, device)
                guidance_added = True
        
        # Add general troubleshooting if no specific guidance was provided
        if not guidance_added:
            enhanced_output += (
                "\n\nGeneral Troubleshooting:"
                "\n- Verify device connectivity and SSH service status"
                "\n- Check credentials and device configuration"
                "\n- Review the debug information below for more details"
            )
        
        enhanced_output += f"\n\nDebug information:\n{error_details}"
        
        return CommandResult(
            command=result.command,
            output=enhanced_output,
            success=False,
            error_message=result.error_message,
            execution_time=result.execution_time
        )
    
    def _get_connection_error_guidance(self, error_message: str, device: Device) -> str:
        """Get guidance for connection errors."""
        hostname = str(device.primary_ip.address.ip) if device.primary_ip else device.name
        
        guidance = "\n\nConnection Error Troubleshooting:"
        
        # Convert to lowercase for case-insensitive matching
        error_lower = error_message.lower()
        
        if "no matching key exchange" in error_lower:
            guidance += (
                "\n- This is an SSH key exchange error"
            )
        elif any(conn_error in error_lower for conn_error in [
            "connection not opened",
            "connection refused", 
            "connection timed out",
            "network is unreachable",
            "no route to host"
        ]):
            guidance += (
                "\n- Verify the device is reachable on the network"
                "\n- Check that SSH service is running on the device"
                "\n- Verify there's no firewall blocking the connection"
                "\n- Ensure the correct NetBox has correct device details (IP, Hostname)"
            )
        elif any(auth_error in error_lower for auth_error in [
            "authentication failed", 
            "all authentication methods failed",
            "permission denied",
            "invalid user",
            "login incorrect",
            "authentication error"
        ]):
            guidance += (
                "\n- Verify username and password are correct"
                "\n- Ensure the user has SSH access permissions on the device"
                "\n- Check if the device requires specific authentication methods"
            )
        elif any(timeout_error in error_lower for timeout_error in [
            "timeout", 
            "timed out",
            "operation timed out"
        ]):
            guidance += (
                "\n- The connection or operation timed out"
                "\n- Check network connectivity to the device"
                "\n- Verify the device is responding"
            )
        else:
            # Generic connection guidance
            guidance += (
                "\n- Verify the device IP address is correct and reachable"
                "\n- Check that SSH service is running on the device (usually port 22)"
                "\n- Verify network connectivity and firewall settings"
                "\n- Ensure your credentials are correct"
            )
        
        guidance += f"\n- Try connecting manually: ssh {hostname}"
        
        return guidance
    
    def _get_bad_descriptor_guidance(self, device: Device) -> str:
        """Get guidance for 'Bad file descriptor' errors."""
        hostname = str(device.primary_ip.address.ip) if device.primary_ip else device.name
        
        return (
            "\n\n'Bad file descriptor' Error Guidance:"
            "\n- This often indicates network connectivity issues"
            "\n- Verify the device IP address is correct"
            "\n- Check that the device is reachable (try pinging it)"
            "\n- Confirm SSH service is running on the device"
            f"\n- Try connecting manually: ssh {hostname}"
        )
    
    def _get_banner_error_guidance(self, device: Device) -> str:
        """Get guidance for SSH banner errors."""
        hostname = str(device.primary_ip.address.ip) if device.primary_ip else device.name
        
        return (
            "\n\nSSH Banner Error Guidance:"
            "\n- The device accepts connections but doesn't provide an SSH banner"
            "\n- This could indicate:"
            "\n  * A different service is running on port 22"
            "\n  * The SSH server is very slow to respond"
            "\n  * A firewall is intercepting the connection"
            "\n  * The SSH implementation is non-standard"
            f"\n- Try manual SSH with verbose logging: ssh -v {hostname}"
            "\n- Check what service is on port 22: nmap -sV -p 22 " + hostname
        )
