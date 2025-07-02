from netbox.plugins import PluginConfig

class ToolkitConfig(PluginConfig):
    name = 'netbox_toolkit_plugin'
    verbose_name = 'Netbox Command Toolkit Plugin'
    description = 'NetBox plugin for running pre-defined commands on network devices'
    version = '0.1.0'
    author = 'Andy Norwood'
    base_url = 'toolkit'

    # Database migrations
    required_settings = []
    
    # Default plugin settings
    default_settings = {
        'rate_limiting_enabled': True,
        'device_command_limit': 10,
        'time_window_minutes': 5,
        'bypass_users': [],
        'bypass_groups': [],
        'debug_logging': False,  # Enable debug logging for this plugin
    }
    
    # Middleware
    middleware = []
    
    # Django apps to load when plugin is activated
    django_apps = []

config = ToolkitConfig