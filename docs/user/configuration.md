# Configuration

This document explains the configuration options available for the NetBox Toolkit Plugin.

## Plugin Configuration

The plugin is configured in NetBox's `configuration.py` file using the `PLUGINS_CONFIG` dictionary. The plugin has been designed with sensible defaults, so **minimal configuration is required**.




```python
# In your NetBox configuration.py
PLUGINS_CONFIG = {
    'netbox_toolkit_plugin': {
        'rate_limiting_enabled': True,      # Enable/disable rate limiting (default: True)
        'device_command_limit': 10,         # Max commands per device per time window (default: 10)
        'time_window_minutes': 5,           # Time window in minutes (default: 5)
        'bypass_users': [],                 # List of usernames who bypass rate limiting (default: [])
        'bypass_groups': [],                # List of group names who bypass rate limiting (default: [])
        'debug_logging': False,             # Enable debug logging for this plugin (default: False)
    },
}
```



### Rate Limiting Configuration

Controls command execution frequency to protect network devices from over utilization.

**Features:**

- Only successful commands are counted toward the rate limit per device within the specified time window
- Failed commands (due to errors, connectivity issues, or syntax problems) do not consume rate limit quota
- When the limit is reached, additional commands are blocked until the window resets
- Users in bypass lists can execute unlimited commands
- Rate limit status is displayed in the device toolkit interface
- Real-time feedback shows remaining commands and time until reset

## Configuration Options

### `rate_limiting_enabled` (boolean)
- **Default**: `True`
- **Purpose**: Enable or disable rate limiting functionality
- **Example**: `'rate_limiting_enabled': False` to disable rate limiting entirely

### `device_command_limit` (integer)
- **Default**: `10`
- **Purpose**: Maximum number of commands allowed per device within the time window
- **Example**: `'device_command_limit': 5` for stricter limiting

### `time_window_minutes` (integer)
- **Default**: `5`
- **Purpose**: Time window in minutes for rate limiting calculations
- **Example**: `'time_window_minutes': 10` for a 10-minute window

### `bypass_users` (list)
- **Default**: `[]` (empty list)
- **Purpose**: List of usernames that bypass rate limiting completely
- **Example**: `'bypass_users': ['admin', 'service_account']`

### `bypass_groups` (list)
- **Default**: `[]` (empty list)
- **Purpose**: List of group names where members bypass rate limiting
- **Example**: `'bypass_groups': ['Network Administrators', 'Senior Engineers']`

### `debug_logging` (boolean)
- **Default**: `False`
- **Purpose**: Enable detailed debug logging for troubleshooting
- **Example**: `'debug_logging': True` to enable verbose logging




**Example Configuration:**
```python
# Allow 15 successful commands per device every 10 minutes, with admin bypass
# Failed commands do not count toward the limit
'rate_limiting_enabled': True,
'device_command_limit': 15,
'time_window_minutes': 10,
'bypass_users': ['admin', 'network_engineer'],
'bypass_groups': ['Network_Admins'],
```

