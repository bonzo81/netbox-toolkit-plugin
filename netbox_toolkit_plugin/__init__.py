from netbox.plugins import PluginConfig

__author__ = "Andy Norwood"
__version__ = "0.1.1"


class ToolkitPluginConfig(PluginConfig):
    """NetBox plugin configuration for the Toolkit plugin."""

    name = "netbox_toolkit_plugin"
    verbose_name = "Command Toolkit Plugin"
    description = "NetBox plugin for running pre-defined commands on network devices"
    version = __version__
    author = __author__
    base_url = "toolkit"
    min_version = "4.2.0"

    # Database migrations
    required_settings = []

    # Default plugin settings
    default_settings = {
        "rate_limiting_enabled": True,
        "device_command_limit": 10,
        "time_window_minutes": 5,
        "bypass_users": [],
        "bypass_groups": [],
        "debug_logging": False,  # Enable debug logging for this plugin
    }


config = ToolkitPluginConfig
