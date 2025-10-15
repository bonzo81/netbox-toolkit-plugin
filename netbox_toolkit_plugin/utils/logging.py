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
            plugins_config = getattr(settings, "PLUGINS_CONFIG", {})
            toolkit_config = plugins_config.get("netbox_toolkit_plugin", {})

            # Check if debug_logging is enabled (default: False)
            return toolkit_config.get("debug_logging", False)
        except (AttributeError, KeyError):
            # If configuration is not available, don't log
            return False


def get_toolkit_logger(name: str) -> logging.Logger:
    """
    Get a logger for the toolkit plugin with the proper namespace and formatting.

    Args:
        name: Logger name (typically __name__)

    Returns:
        Logger instance for the toolkit plugin with timestamped formatting
    """
    # Ensure we're using the netbox_toolkit_plugin namespace
    if not name.startswith("netbox_toolkit_plugin"):
        if name == "__main__":
            name = "netbox_toolkit_plugin"
        else:
            # Extract module name and add to toolkit namespace
            module_parts = name.split(".")
            if "netbox_toolkit" in module_parts:
                # Already in our namespace, use as-is
                pass
            else:
                # Add to our namespace
                name = f"netbox_toolkit.{name.split('.')[-1]}"

    logger = logging.getLogger(name)

    # Configure timestamped formatting if not already configured
    if not logger.handlers and (not logger.parent or not logger.parent.handlers):
        _configure_plugin_logging(logger)

    return logger


def _configure_plugin_logging(logger: logging.Logger) -> None:
    """
    Configure plugin-specific logging with timestamps matching NetBox format.

    Simple approach:
    - Default: INFO level (shows command execution, warnings, errors)
    - Debug mode: DEBUG level when debug_logging=True in plugin config

    Args:
        logger: Logger instance to configure
    """
    # Only configure if no handlers exist (avoid duplicate configuration)
    if logger.handlers:
        return

    # Check if debug logging is enabled in plugin configuration
    debug_enabled = _is_debug_logging_enabled()

    # Create console handler
    handler = logging.StreamHandler()

    # Set level based on debug mode
    if debug_enabled:
        handler.setLevel(logging.DEBUG)
        logger.setLevel(logging.DEBUG)
        log_format = "[%(asctime)s] %(levelname)s %(name)s: %(message)s"
    else:
        handler.setLevel(logging.INFO)
        logger.setLevel(logging.INFO)
        log_format = "[%(asctime)s] %(levelname)s %(name)s: %(message)s"

    # Create formatter with timestamp matching NetBox server logs format
    formatter = logging.Formatter(fmt=log_format, datefmt="%d/%b/%Y %H:%M:%S")
    handler.setFormatter(formatter)

    # Add handler to logger
    logger.addHandler(handler)
    logger.propagate = False  # Don't propagate to parent loggers


def _is_debug_logging_enabled() -> bool:
    """
    Check if debug logging is enabled in plugin configuration.

    Returns:
        bool: True if debug_logging is enabled in plugin config
    """
    try:
        from django.conf import settings

        plugins_config = getattr(settings, "PLUGINS_CONFIG", {})
        toolkit_config = plugins_config.get("netbox_toolkit_plugin", {})
        return toolkit_config.get("debug_logging", False)
    except (AttributeError, ImportError):
        return False
