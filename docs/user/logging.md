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

### Step 2: Run NetBox in Foreground (Development)

```bash
python manage.py runserver 0.0.0.0:8000
```

That's it! You'll now see plugin messages like:
```
[24/Sep/2025 10:05:21] INFO netbox_toolkit_plugin.connectors.netmiko_connector: DEVICE_COMMAND: Sending show command to router01: 'show version'
[24/Sep/2025 10:05:20] WARNING netbox_toolkit_plugin.services.command_service: Connection attempt 1 failed for test-switch-01 (fast-failing to Netmiko): No matching key exchange found
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
- Error analysis

## What You'll See

### Normal Mode (INFO level)
- ✅ Commands being sent to devices
- ⚠️ Connection issues and retries
- ❌ Authentication and execution failures

### Debug Mode (DEBUG level)
- All of the above, plus:
- Connection parameter details
- Retry logic and timing
- Connector selection process
- Detailed error analysis

## Production Use

For production environments:
- Use **Normal Mode** (INFO level)
- Consider logging to files instead of console
- The `debug_logging: False` (default) keeps logs minimal

## Turn Off Logging

To disable plugin logging entirely, either:
1. Remove the `LOGGING` configuration from `configuration.py`, or
2. Set `debug_logging: False` in `PLUGINS_CONFIG` and use WARNING level:

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'WARNING',  # Only show warnings and errors
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'WARNING',
    },
}
```

## Summary

- **Default**: Plugin works silently (no NetBox logging configured)
- **Troubleshooting**: Add basic `LOGGING` config to see command execution and issues
- **Deep Debugging**: Add `debug_logging: True` for detailed troubleshooting information

The plugin handles all the formatting and timestamps automatically - you just need to tell NetBox to show the logs.