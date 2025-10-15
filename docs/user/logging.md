# NetBox Toolkit Plugin - Logging Guide

## Quick Setup (Most Users)

The plugin automatically logs important messages. To see them, you just need to enable console output in NetBox.

### Step 1: Enable NetBox Console Logging

Add this to your NetBox `configuration.py` file:

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'INFO',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}
```


## Debug Mode (Troubleshooting)

If you need more detailed logging for troubleshooting, add this to your NetBox `configuration.py`:

```python
# Plugin configuration - enable debug logging
PLUGINS_CONFIG = {
    'netbox_toolkit_plugin': {
        'debug_logging': True,  # Enable detailed debug messages

        # Your other plugin settings...
        'rate_limiting_enabled': True,
        'device_command_limit': 10,
        'time_window_minutes': 5,
    }
}

# Basic logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG',  # Show debug messages
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'DEBUG',
    },
}
```

With debug mode enabled, you'll see detailed messages about:

- Connection attempts and retries
- Command execution timing
- Configuration details



### Normal Mode (INFO level)
- ✅ Commands being sent to devices
- ⚠️ Connection issues and retries
- ❌ Authentication and execution failures

### Debug Mode (DEBUG level)
- All of the above, plus:

- Connection parameter details
- Retry logic and timing
- Connector selection process



## Summary

- **Default**: Plugin works silently (no NetBox logging configured)
- **Troubleshooting**: Add basic `LOGGING` config to see command execution and issues
- **Deep Debugging**: Add `debug_logging: True` for detailed troubleshooting information

