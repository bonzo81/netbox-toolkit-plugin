# Installation

This guide explains how to install the NetBox Toolkit Plugin in your NetBox environment.

## Installation Steps

First activate your virtual environment and install the plugin:

```bash
source /opt/netbox/venv/bin/activate
```

### 1. **Install the Plugin**
```bash
pip install netbox-toolkit-plugin
```

### 2. **Enable in NetBox**
Add `'netbox_toolkit'` to `PLUGINS` in your NetBox configuration
```python
# In your NetBox configuration.py
PLUGINS = [
    'netbox_toolkit',
    # ... other plugins
]

PLUGINS_CONFIG = {
    'netbox_toolkit': {
        'rate_limiting_enabled': True,      # Enable/disable rate limiting (default: True)
        'device_command_limit': 10,         # Max commands per device per time window (default: 10)
        'time_window_minutes': 5,           # Time window in minutes (default: 5)
        'bypass_users': [],                 # List of usernames who bypass rate limiting (default: [])
        'bypass_groups': [],                # List of group names who bypass rate limiting (default: [])
        'debug_logging': False,             # Enable debug logging for this plugin (default: False)
    },
}
```
**See [Plugin Configuration](./configuration.md) for more details.**

### 3. **Run Database Migrations**

Apply the database migrations to create the necessary tables:

```bash
cd /opt/netbox/netbox
python3 manage.py migrate netbox_toolkit
```

### 4. **Collect Static Files**

Collect static files to ensure the plugin's CSS and JavaScript are properly served:

```bash
cd /opt/netbox/netbox
python3 manage.py collectstatic
```

### 5. **Restart NetBox Services**

Restart the NetBox services to apply the changes:

```bash
sudo systemctl restart netbox netbox-rq
```

##Next Steps:

- [Create commands](./command-creation.md)
- [Set up permissions](./permissions-setup-guide.md)
- [Debug logging](./debug-logging.md) (Optional)

## Upgrading

To upgrade to a newer version of the plugin:

1. Install the new version:
   ```bash
   pip install --upgrade netbox-toolkit-plugin
   ```

2. Apply any new migrations:
   ```bash
   cd /opt/netbox/netbox
   python3 manage.py migrate netbox_toolkit
   ```

3. Collect static files:
   ```bash
   python3 manage.py collectstatic
   ```

4. Restart NetBox services:
   ```bash
   sudo systemctl restart netbox netbox-rq
   ```
