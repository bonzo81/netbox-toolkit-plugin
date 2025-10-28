from django.core.exceptions import ImproperlyConfigured

from netbox.plugins import PluginConfig

__author__ = "Andy Norwood"
__version__ = "0.1.5"


class ToolkitPluginConfig(PluginConfig):
    """NetBox plugin configuration for the Toolkit plugin."""

    name = "netbox_toolkit_plugin"
    verbose_name = "Toolkit Plugin"
    description = "NetBox plugin for running pre-defined commands on network devices"
    version = __version__
    author = __author__
    base_url = "toolkit"
    min_version = "4.2.0"

    # Database migrations
    required_settings = []  # Custom validation in ready() method

    # Default plugin settings
    default_settings = {
        "rate_limiting_enabled": True,
        "device_command_limit": 10,
        "time_window_minutes": 5,
        "bypass_users": [],
        "bypass_groups": [],
        "debug_logging": False,  # Enable debug logging for this plugin
    }

    def ready(self):
        """
        Validate plugin configuration at startup.

        This runs when Django initializes the app registry, ensuring
        critical settings (like the security pepper) are configured
        before NetBox starts accepting requests.
        """
        super().ready()

        # Validate security configuration (including pepper requirement)
        from .settings import ToolkitSettings

        try:
            ToolkitSettings.get_security_config()
        except ValueError as e:
            # Re-raise as ImproperlyConfigured for Django consistency
            raise ImproperlyConfigured(
                f"Plugin {self.name} configuration error: {str(e)}"
            ) from e


config = ToolkitPluginConfig
