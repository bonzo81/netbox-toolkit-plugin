"""Service for handling command execution on devices."""

from typing import Any

from dcim.models import Device

from ..connectors.base import CommandResult
from ..connectors.factory import ConnectorFactory
from ..connectors.netmiko_connector import NetmikoConnector
from ..exceptions import DeviceConnectionError
from ..models import Command, CommandLog
from ..settings import ToolkitSettings
from ..utils.logging import get_toolkit_logger

logger = get_toolkit_logger(__name__)


class CommandExecutionService:
    """Service for executing commands on devices."""

    def __init__(self):
        self.connector_factory = ConnectorFactory()

    def execute_command_with_retry(
        self,
        command: "Command",
        device: Any,
        username: str,
        password: str,
        max_retries: int = 1,
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

        logger.info(
            "Executing command '%s' on device %s (max_retries=%s)",
            command.name,
            device.name,
            max_retries,
        )

        for attempt in range(max_retries + 1):
            try:
                logger.debug(
                    "Attempt %d/%d for command execution", attempt + 1, max_retries + 1
                )

                # Create appropriate connector for the device
                connector = self.connector_factory.create_connector(
                    device, username, password
                )
                logger.debug(
                    "Created %s connector for device %s",
                    type(connector).__name__,
                    device.name,
                )

                # Execute command using context manager for proper cleanup
                with connector:
                    result = connector.execute_command(
                        command.command, command.command_type
                    )
                    logger.debug(
                        "Command executed successfully, output length: %d chars",
                        len(result.output) if result.output else 0,
                    )

                # If successful, log and return
                logger.info(
                    "Command execution completed successfully on %s", device.name
                )
                command_log = self._log_command_execution(
                    command, device, result, username
                )
                result.command_log_id = command_log.id
                return result

            except Exception as e:
                last_error = e
                error_msg = str(e)

                # Distinguish between connection failures and command execution failures
                if (
                    "Fast-fail to Netmiko" in error_msg
                    or ToolkitSettings.should_fast_fail_to_netmiko(error_msg)
                ):
                    # Extract the original error message from the fast-fail wrapper
                    if "Fast-fail to Netmiko:" in error_msg:
                        original_error = error_msg.split("Fast-fail to Netmiko:", 1)[
                            1
                        ].strip()
                        logger.warning(
                            "Connection attempt %d failed for %s (fast-failing to Netmiko): %s",
                            attempt + 1,
                            device.name,
                            original_error,
                        )
                    else:
                        logger.warning(
                            "Connection attempt %d failed for %s (fast-failing to Netmiko): %s",
                            attempt + 1,
                            device.name,
                            error_msg,
                        )
                else:
                    logger.warning(
                        "Command execution attempt %d failed for %s: %s",
                        attempt + 1,
                        device.name,
                        error_msg,
                    )

                # Check for authentication errors and fail fast with clear message
                # Only fail fast for explicit auth failures, not transient connection issues
                if self._is_authentication_error(error_msg):
                    logger.error(
                        "Authentication failure detected for device %s",
                        device.name,
                    )
                    # Create a failed result with authentication error details
                    auth_failed_result = CommandResult(
                        command=command.command,
                        output="",
                        success=False,
                        error_message=f"Authentication failed: {error_msg}",
                    )
                    # Enhance the error result with troubleshooting guidance
                    auth_failed_result = self._enhance_error_result(
                        auth_failed_result, e, device
                    )
                    command_log = self._log_command_execution(
                        command, device, auth_failed_result, username
                    )
                    auth_failed_result.command_log_id = command_log.id
                    # Return the failed result instead of raising an exception
                    # This allows the web interface to handle it gracefully
                    return auth_failed_result

                # Log if this is a retryable connection error
                if self._is_connection_error(error_msg):
                    logger.info(
                        "Transient connection error detected for device %s - will retry",
                        device.name,
                    )

                # Check for fast-fail scenario and automatically retry with Netmiko
                if (
                    "Fast-fail to Netmiko" in error_msg
                    or ToolkitSettings.should_fast_fail_to_netmiko(error_msg)
                ):
                    logger.info(
                        "Fast-fail pattern detected, attempting fallback to Netmiko for device %s",
                        device.name,
                    )
                    try:
                        # Create Netmiko connector directly for fallback
                        base_config = self.connector_factory._build_connection_config(
                            device, username, password
                        )
                        netmiko_config = (
                            self.connector_factory._prepare_connector_config(
                                base_config, NetmikoConnector
                            )
                        )
                        fallback_connector = NetmikoConnector(netmiko_config)

                        # Execute command using Netmiko fallback connector
                        with fallback_connector:
                            result = fallback_connector.execute_command(
                                command.command, command.command_type
                            )
                            logger.info(
                                "Command executed successfully using Netmiko fallback on %s",
                                device.name,
                            )
                            command_log = self._log_command_execution(
                                command, device, result, username
                            )
                            result.command_log_id = command_log.id
                            return result

                    except Exception as fallback_error:
                        logger.warning(
                            "Netmiko fallback also failed for device %s",
                            device.name,
                        )
                        last_error = fallback_error
                        break  # Don't retry after fallback failure

                # If this was a socket/connection error and we have retries left, continue
                elif attempt < max_retries and (
                    "socket" in error_msg.lower()
                    or "connection" in error_msg.lower()
                    or "Bad file descriptor" in error_msg
                ):
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
            error_message=str(last_error) if last_error else "Unknown error",
        )

        # Add detailed error information if we have an error
        if last_error:
            error_result = self._enhance_error_result(error_result, last_error, device)

        # Log the failed execution
        command_log = self._log_command_execution(
            command, device, error_result, username
        )
        error_result.command_log_id = command_log.id

        return error_result

    def execute_command_with_token(
        self,
        command: "Command",
        device: Any,
        credential_token: str,
        user,
        max_retries: int = 1,
    ) -> "CommandResult":
        """
        Execute a command using stored credentials via token.

        Args:
            command: Command to execute
            device: Target device
            credential_token: Credential token for stored credentials
            user: User requesting the execution
            max_retries: Maximum number of retry attempts

        Returns:
            CommandResult with execution details
        """
        from .credential_service import CredentialService

        credential_service = CredentialService()

        # Get credentials using token
        success, credentials, credential_set, error = (
            credential_service.get_credentials_for_device(
                credential_token, user, device
            )
        )

        if not success:
            logger.error(
                "Failed to retrieve credentials for token-based execution: %s", error
            )
            # Return error result
            error_result = CommandResult(
                command=command.command,
                output="",
                success=False,
                error_message=f"Credential retrieval failed: {error}",
                execution_time=0.0,
            )
            return self._enhance_error_result(error_result, Exception(error), device)

        logger.info(
            "Executing command '%s' on device %s using credential set '%s'",
            command.name,
            device.name,
            credential_set.name,
        )

        # Execute using the retrieved credentials
        return self.execute_command_with_retry(
            command=command,
            device=device,
            username=credentials["username"],
            password=credentials["password"],
            max_retries=max_retries,
        )

    def execute_command_with_credential_set(
        self,
        command: "Command",
        device: Any,
        credential_set_id: int,
        user,
        max_retries: int = 1,
    ) -> "CommandResult":
        """
        Execute a command using a credential set ID directly.

        Args:
            command: Command to execute
            device: Target device
            credential_set_id: ID of the credential set to use
            user: User requesting the execution
            max_retries: Maximum number of retry attempts

        Returns:
            CommandResult with execution details
        """
        from ..models import DeviceCredentialSet

        logger.info(
            "Executing command '%s' on device %s using credential set ID %s",
            command.name,
            device.name,
            credential_set_id,
        )

        try:
            # Get the credential set
            credential_set = DeviceCredentialSet.objects.get(
                id=credential_set_id, owner=user
            )
        except DeviceCredentialSet.DoesNotExist:
            error_result = CommandResult(
                command=command.command,
                output="",
                success=False,
                error_message="Credential set not found or access denied",
                execution_time=0.0,
            )
            return self._enhance_error_result(
                error_result, Exception("Credential set not found"), device
            )

        # Decrypt credentials directly
        from .encryption_service import CredentialEncryptionService

        encryption_service = CredentialEncryptionService()
        try:
            credentials = encryption_service.decrypt_credentials(
                credential_set.encrypted_username,
                credential_set.encrypted_password,
                credential_set.encryption_key_id,
            )
        except Exception as e:
            error_result = CommandResult(
                command=command.command,
                output="",
                success=False,
                error_message=f"Failed to decrypt credentials: {str(e)}",
                execution_time=0.0,
            )
            return self._enhance_error_result(error_result, e, device)

        # Execute using the decrypted credentials
        return self.execute_command_with_retry(
            command=command,
            device=device,
            username=credentials["username"],
            password=credentials["password"],
            max_retries=max_retries,
        )

    def _log_command_execution(
        self, command: Command, device: Device, result: CommandResult, username: str
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
            # For failed commands, log a concise technical message rather than the user-friendly guidance
            # Extract just the core error from the enhanced user message
            core_error = result.error_message or "Unknown error"

            # If result.output contains user guidance, extract just the first line for logging
            if result.output and "\n\n" in result.output:
                # Take just the first part before user guidance starts
                log_output = result.output.split("\n\n")[0]
            else:
                log_output = core_error

            output = f"Command execution failed: {log_output}"
            success = False
            error_message = core_error

        # Create log entry with concise technical details
        command_log = CommandLog.objects.create(
            command=command,
            device=device,
            output=output,
            username=username,
            success=success,
            error_message=error_message,
            execution_duration=result.execution_time,
        )

        if result.has_syntax_error:
            pass  # Syntax error detected but not logging
        else:
            pass  # Command executed successfully but not logging

        return command_log

    def _enhance_error_result(
        self, result: CommandResult, error: Exception, device: Device
    ) -> CommandResult:
        """Enhance error result with user-friendly troubleshooting information."""
        error_message = str(error)

        # For DeviceConnectionError, the connector has already provided a formatted message
        # with guidance, so we just need to clean it up for user display
        if isinstance(error, DeviceConnectionError):
            enhanced_output = error_message

            # Remove any duplicate "Authentication failed for" prefixes that might occur
            if (
                enhanced_output.startswith("Authentication failed for")
                and "Authentication failed for" in enhanced_output[25:]
            ):
                # Find the second occurrence and use everything from there
                second_occurrence = enhanced_output.find(
                    "Authentication failed for", 25
                )
                if second_occurrence != -1:
                    enhanced_output = enhanced_output[second_occurrence:]

        else:
            # For other errors, provide basic error info with guidance
            enhanced_output = f"Command execution failed: {error_message}"

            # Add specific guidance for common non-connection errors
            if "Bad file descriptor" in str(error):
                enhanced_output += self._get_bad_descriptor_guidance(device)
            elif "Error reading SSH protocol banner" in str(error):
                enhanced_output += self._get_banner_error_guidance(device)
            elif any(
                error_term in error_message.lower()
                for error_term in [
                    "connect",
                    "connection",
                    "authentication",
                    "failed to connect",
                    "ssh",
                    "timeout",
                    "unreachable",
                    "refused",
                ]
            ):
                enhanced_output += self._get_connection_error_guidance(
                    error_message, device
                )
            else:
                # Generic troubleshooting for unknown errors
                enhanced_output += (
                    "\n\nTroubleshooting:"
                    "\n- Verify device connectivity and SSH service status"
                    "\n- Check credentials and device configuration"
                    "\n- Ensure the device is reachable and responding"
                )

        return CommandResult(
            command=result.command,
            output=enhanced_output,
            success=False,
            error_message=result.error_message,
            execution_time=result.execution_time,
        )

    def _get_connection_error_guidance(self, error_message: str, device: Device) -> str:
        """Get guidance for connection errors."""
        hostname = (
            str(device.primary_ip.address.ip) if device.primary_ip else device.name
        )

        guidance = "\n\nConnection Error Troubleshooting:"

        # Convert to lowercase for case-insensitive matching
        error_lower = error_message.lower()

        if "no matching key exchange" in error_lower:
            guidance += "\n- This is an SSH key exchange error"
        elif any(
            conn_error in error_lower
            for conn_error in [
                "connection not opened",
                "connection refused",
                "connection timed out",
                "network is unreachable",
                "no route to host",
            ]
        ):
            guidance += (
                "\n- Verify the device is reachable on the network"
                "\n- Check that SSH service is running on the device"
                "\n- Verify there's no firewall blocking the connection"
                "\n- Ensure the correct NetBox has correct device details (IP, Hostname)"
            )
        elif any(
            auth_error in error_lower
            for auth_error in [
                "authentication failed",
                "all authentication methods failed",
                "permission denied",
                "invalid user",
                "login incorrect",
                "authentication error",
            ]
        ):
            guidance += (
                "\n- Verify username and password are correct"
                "\n- Ensure the user has SSH access permissions on the device"
                "\n- Check if the device requires specific authentication methods"
            )
        elif any(
            timeout_error in error_lower
            for timeout_error in ["timeout", "timed out", "operation timed out"]
        ):
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

    def _is_authentication_error(self, error_message: str) -> bool:
        """
        Detect if an error message indicates authentication failure.

        Only returns True for explicit authentication rejections, not transient
        network errors that should be retried.

        Returns:
            True if the error is a definite authentication failure
        """
        error_lower = error_message.lower()

        # Explicit authentication failure patterns only
        # These indicate wrong credentials, not transient network issues
        auth_patterns = [
            "password prompt seen more than once",
            "authentication failed",
            "auth failed",
            "login failed",
            "access denied",
            "permission denied",
            "authentication error",
            "invalid password",
            "invalid username",
            "login incorrect",
            "authentication timeout",
            "too many authentication failures",
            "authentication attempts exceeded",
            # SSH-specific auth failures
            "ssh handshake failed",
            "ssh authentication failed",
            "publickey authentication failed",
            "password authentication failed",
            "keyboard-interactive authentication failed",
        ]

        # Check if any authentication pattern is found
        for pattern in auth_patterns:
            if pattern in error_lower:
                logger.debug(
                    f"Authentication error pattern detected: '{pattern}' in '{error_message}'"
                )
                return True

        return False

    def _is_connection_error(self, error_message: str) -> bool:
        """
        Detect if an error message indicates a transient connection issue.

        These errors may succeed on retry and should not be treated as
        authentication failures.

        Returns:
            True if the error is a transient connection issue
        """
        error_lower = error_message.lower()

        # Connection-level errors that are often transient
        connection_patterns = [
            "encountered eof reading from transport",
            "connection closed by peer",
            "connection reset by peer",
            "connection timed out",
            "connection refused",
            "network is unreachable",
            "host is unreachable",
            "socket error",
            "broken pipe",
        ]

        for pattern in connection_patterns:
            if pattern in error_lower:
                logger.debug(
                    f"Connection error pattern detected: '{pattern}' in '{error_message}'"
                )
                return True

        return False

    def _get_bad_descriptor_guidance(self, device: Device) -> str:
        """Get guidance for 'Bad file descriptor' errors."""
        hostname = (
            str(device.primary_ip.address.ip) if device.primary_ip else device.name
        )

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
        hostname = (
            str(device.primary_ip.address.ip) if device.primary_ip else device.name
        )

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
