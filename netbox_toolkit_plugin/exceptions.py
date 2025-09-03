"""Custom exceptions for the NetBox Toolkit plugin."""


class ToolkitError(Exception):
    """Base exception for toolkit-related errors."""


class DeviceConnectionError(ToolkitError):
    """Raised when device connection fails."""


class DeviceReachabilityError(DeviceConnectionError):
    """Raised when device is not reachable."""


class SSHBannerError(DeviceConnectionError):
    """Raised when SSH banner issues occur."""


class AuthenticationError(DeviceConnectionError):
    """Raised when authentication fails."""


class CommandExecutionError(ToolkitError):
    """Raised when command execution fails."""


class UnsupportedPlatformError(ToolkitError):
    """Raised when device platform is not supported."""
