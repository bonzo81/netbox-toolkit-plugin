"""Custom exceptions for the NetBox Toolkit plugin."""


class ToolkitError(Exception):
    """Base exception for toolkit-related errors."""
    pass


class DeviceConnectionError(ToolkitError):
    """Raised when device connection fails."""
    pass


class DeviceReachabilityError(DeviceConnectionError):
    """Raised when device is not reachable."""
    pass


class SSHBannerError(DeviceConnectionError):
    """Raised when SSH banner issues occur."""
    pass


class AuthenticationError(DeviceConnectionError):
    """Raised when authentication fails."""
    pass


class CommandExecutionError(ToolkitError):
    """Raised when command execution fails."""
    pass


class UnsupportedPlatformError(ToolkitError):
    """Raised when device platform is not supported."""
    pass
