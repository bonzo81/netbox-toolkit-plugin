"""Logging utilities for NetBox Toolkit plugin."""
import logging
from django.conf import settings


class RequireToolkitDebug(logging.Filter):
    """
    Custom logging filter that only allows log records when the plugin's 
    debug_logging setting is enabled.
    
    This allows plugin-specific debug logging without requiring Django's 
    DEBUG=True, making it safe for production environments.
    """
    
    def filter(self, record):
        """
        Check if toolkit debug logging is enabled.
        
        Returns:
            bool: True if debug logging is enabled for this plugin
        """
        try:
            # Get plugin configuration from Django settings
            plugins_config = getattr(settings, 'PLUGINS_CONFIG', {})
            toolkit_config = plugins_config.get('netbox_toolkit', {})
            
            # Check if debug_logging is enabled (default: False)
            return toolkit_config.get('debug_logging', False)
        except (AttributeError, KeyError):
            # If configuration is not available, don't log
            return False


def get_toolkit_logger(name: str) -> logging.Logger:
    """
    Get a logger for the toolkit plugin with the proper namespace.
    
    Args:
        name: Logger name (typically __name__)
        
    Returns:
        Logger instance for the toolkit plugin
    """
    # Ensure we're using the netbox_toolkit namespace
    if not name.startswith('netbox_toolkit'):
        if name == '__main__':
            name = 'netbox_toolkit'
        else:
            # Extract module name and add to toolkit namespace
            module_parts = name.split('.')
            if 'netbox_toolkit' in module_parts:
                # Already in our namespace, use as-is
                pass
            else:
                # Add to our namespace
                name = f'netbox_toolkit.{name.split(".")[-1]}'
    
    return logging.getLogger(name)
