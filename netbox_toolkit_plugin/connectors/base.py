"""Base connector interface for device connections."""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from dataclasses import dataclass

from ..exceptions import DeviceConnectionError, CommandExecutionError


@dataclass
class ConnectionConfig:
    """Configuration for device connections."""
    hostname: str
    username: str
    password: str
    port: int = 22
    timeout_socket: int = 15
    timeout_transport: int = 15
    timeout_ops: int = 30
    auth_strict_key: bool = False
    transport: str = 'system'  # Default to system transport for Scrapli
    platform: Optional[str] = None
    extra_options: Optional[Dict[str, Any]] = None


@dataclass
class CommandResult:
    """Result of command execution."""
    command: str
    output: str
    success: bool
    error_message: Optional[str] = None
    execution_time: Optional[float] = None
    # New fields for syntax error detection
    has_syntax_error: bool = False
    syntax_error_type: Optional[str] = None
    syntax_error_vendor: Optional[str] = None
    syntax_error_guidance: Optional[str] = None
    # New fields for command output parsing
    parsed_output: Optional[Dict[str, Any]] = None
    parsing_success: bool = False
    parsing_method: Optional[str] = None  # 'textfsm', 'genie', 'ttp'
    parsing_error: Optional[str] = None


class BaseDeviceConnector(ABC):
    """Abstract base class for device connectors."""
    
    def __init__(self, config: ConnectionConfig):
        self.config = config
        self._connection = None
    
    @abstractmethod
    def connect(self) -> None:
        """Establish connection to the device."""
        pass
    
    @abstractmethod
    def disconnect(self) -> None:
        """Close connection to the device."""
        pass
    
    @abstractmethod
    def execute_command(self, command: str, command_type: str = 'show') -> CommandResult:
        """Execute a command on the device.
        
        Args:
            command: The command string to execute
            command_type: Type of command ('show' or 'config') for proper handling
            
        Returns:
            CommandResult with execution details
        """
        pass
    
    @abstractmethod
    def is_connected(self) -> bool:
        """Check if connection is active."""
        pass
    
    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()
    
    @property
    def hostname(self) -> str:
        """Get the hostname for this connection."""
        return self.config.hostname
    
    @property
    def platform(self) -> Optional[str]:
        """Get the platform for this connection."""
        return self.config.platform
