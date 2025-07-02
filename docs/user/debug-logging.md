# NetBox Toolkit Plugin - Debug Logging Configuration

Add this configuration to your NetBox `configuration.py` file to enable debug logging for the NetBox Toolkit plugin.

## Enable Plugin Debug Logging

```python
# Plugin configuration
PLUGINS_CONFIG = {
    'netbox_toolkit': {
        # Enable debug logging for the toolkit plugin
        'debug_logging': True,
        
        # Your other plugin settings...
        'rate_limiting_enabled': True,
        'device_command_limit': 10,
        'time_window_minutes': 5,
    }
}

# Logging configuration for NetBox Toolkit plugin
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {  # Define how log messages are formatted
        'toolkit_debug': {
            'format': '[TOOLKIT] {levelname} {asctime} {name} - {message}',
            'style': '{',
        },
    },
    'filters': {  # Control which log messages are processed
        'require_toolkit_debug': {
            '()': 'netbox_toolkit.utils.logging.RequireToolkitDebug',
        },
    },
    'handlers': {  # Define where log messages are sent (console, file, etc.)
        'toolkit_console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'toolkit_debug',
            'filters': ['require_toolkit_debug'],
        },
    },
    'loggers': {  # Configure which modules send logs and at what level
        'netbox_toolkit': {
            'handlers': ['toolkit_console'],
            'level': 'DEBUG',
            'propagate': False,  # Don't send to parent loggers
        },
    },
}
```

## Log Levels

You can adjust the logging level based on your needs:

- `DEBUG`: All messages (very verbose, shows connection attempts, command execution details)
- `INFO`: Informational messages (successful connections, command completions)
- `WARNING`: Warning messages (connection issues, non-critical errors)
- `ERROR`: Error messages only (failed connections, command failures)

Example for less verbose logging:
```python
'loggers': {
    'netbox_toolkit': {
        'handlers': ['toolkit_console'],
        'level': 'INFO',  # Less verbose than DEBUG
        'propagate': False,
    },
}
```

## Usage Notes

1. **Production Safety**: This logging configuration is safe for production because it only activates when `debug_logging: True` is set in the plugin configuration.

2. **Performance**: When `debug_logging: False` (default), debug messages are filtered out at the handler level, minimizing performance impact.

3. **Integration**: Command Toolkit plugin logging integrates with your existing NetBox logging configuration and won't interfere with other NetBox logs.

## Disable Plugin Debug Logging

To disable plugin debug logging, simply set:
```python
PLUGINS_CONFIG = {
    'netbox_toolkit': {
        'debug_logging': False,  # Disable debug logging
    }
}
```

Or remove the `debug_logging` setting entirely (default is `False`).

## Example Log Output

When enabled, you'll see detailed logging like:
```
[TOOLKIT] DEBUG 2025-06-05 10:30:15 netbox_toolkit.connectors.factory - Creating connector for device router-01 with platform cisco_ios
[TOOLKIT] DEBUG 2025-06-05 10:30:15 netbox_toolkit.connectors.scrapli_connector - Attempting to connect to 192.168.1.1:22
[TOOLKIT] INFO 2025-06-05 10:30:16 netbox_toolkit.connectors.scrapli_connector - Successfully connected to 192.168.1.1 using IOSXEDriver
[TOOLKIT] DEBUG 2025-06-05 10:30:16 netbox_toolkit.services.command_service - Executing show command: show version
[TOOLKIT] DEBUG 2025-06-05 10:30:17 netbox_toolkit.services.command_service - Command completed successfully in 0.8s
```
