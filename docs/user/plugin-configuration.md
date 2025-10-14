# Plugin Configuration

## Overview

The NetBox Toolkit Plugin is configured through NetBox's standard `PLUGINS_CONFIG` dictionary in your `configuration.py` file.

**⚠️ REQUIRED**: A security pepper must be configured (see Security Pepper section below). All other settings have sensible defaults.

## Basic Configuration

### Minimal Setup (Required)

```python
# In your NetBox configuration.py
PLUGINS = [
    'netbox_toolkit_plugin',
    # ... other plugins
]

# REQUIRED: Security pepper configuration
PLUGINS_CONFIG = {
    'netbox_toolkit_plugin': {
        'security': {
            'pepper': 'your-secure-pepper-value-minimum-32-chars',  # REQUIRED
        },
    },
}
```

### Full Configuration (All Options)

```python
PLUGINS_CONFIG = {
    'netbox_toolkit_plugin': {
        # REQUIRED
        'security': {
            'pepper': 'your-secure-pepper-value-minimum-32-chars',
        },
        # OPTIONAL - Rate limiting settings (showing defaults)
        'rate_limiting_enabled': True,
        'device_command_limit': 10,
        'time_window_minutes': 5,
        'bypass_users': [],
        'bypass_groups': [],
        'debug_logging': False,
    },
}
```

## Rate Limiting Configuration

### Why Rate Limiting
Rate limiting prevents network devices from being overwhelmed by excessive command execution, which can:

- Impact device performance and stability
- Interfere with production traffic
- Trigger device protection mechanisms
- Create security audit concerns

### How It Works
- **Protection Window**: When limit is reached, additional commands are blocked until the time window resets
- **Bypass Capability**: Designated users and groups can execute unlimited commands for emergency situations
- **Real-time Feedback**: Rate limit status is displayed in the device toolkit interface

## Rate Limiting Configuration Options

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

## Security Configuration

### Overview
The plugin uses **Argon2id** for secure credential token hashing and **Fernet encryption** for storing device credentials. A security pepper is **required** for enhanced protection.

### Security Pepper (REQUIRED)

**⚠️ CRITICAL**: You must configure a security pepper before using the plugin.

Choose the method that best fits your deployment:

---

#### **Method 1: Configuration File**

First, generate a secure pepper:

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(48))"
```

Then add it directly to your NetBox `configuration.py`:

```python
PLUGINS_CONFIG = {
    'netbox_toolkit_plugin': {
        'security': {
            'pepper': 'your-secure-pepper-value-minimum-32-chars',
        },
    },
}
```

**✅ Pros:** Simple, persistent across reboots
**❌ Cons:** Visible in config file, risk of version control exposure

**Security Notes:**
- Never commit `configuration.py` with pepper to version control
- Ensure proper file permissions: `chmod 640 /opt/netbox/netbox/netbox/configuration.py`
- Consider using a separate secrets file that's excluded from git

---

#### **Method 2: Environment Variable**

```bash
# 1. Generate a secure pepper
python3 -c "import secrets; print(secrets.token_urlsafe(48))"

# 2. Export in the shell where NetBox runs
export NETBOX_TOOLKIT_PEPPER="your-generated-pepper-here"

# 3. Restart NetBox
sudo systemctl restart netbox netbox-rq
```

**✅ Pros:** Keeps pepper out of code, better for version control
**❌ Cons:** Lost on reboot/logout (credentials must be recreated)

**⚠️ Important:**
- This method only works if NetBox is run from the same shell session
- With systemd, the export won't persist - use Method 1 for production
- If the environment variable is lost, all credential tokens become invalid

---

#### **Docker/Docker Compose**

For containerized deployments:

```yaml
# docker-compose.yml
services:
  netbox:
    environment:
      - NETBOX_TOOLKIT_PEPPER=your-generated-pepper-here
```

Or use a `.env` file:
```bash
# .env file (same directory as docker-compose.yml)
NETBOX_TOOLKIT_PEPPER=your-generated-pepper-here
```

**Note:** Docker environment variables persist across container restarts and system reboots.

---

### Quick Comparison

| Method | Persistent | Setup | Best For |
|--------|-----------|--------|----------|
| **Config File** | ✅ Yes | Simple | Production |
| **Export** | ❌ No* | Simple | Testing/Dev |
| **Docker** | ✅ Yes | Simple | Containers |

*Lost on reboot/logout
```python
PLUGINS_CONFIG = {
    'netbox_toolkit_plugin': {
        'security': {
            'pepper': 'your-secure-pepper-value-minimum-32-chars',
        },
    },
}
```

**⚠️ Important Security Notes:**
- Pepper must be at least 32 characters long
- Never commit the pepper to version control
- Use environment variable for production deployments
- Changing the pepper will invalidate all existing credential tokens

### Argon2id Configuration (Optional)

Fine-tune the Argon2id password hashing parameters:

```python
PLUGINS_CONFIG = {
    'netbox_toolkit_plugin': {
        'security': {
            'argon2': {
                'time_cost': 3,        # Number of iterations (higher = more secure, slower)
                'memory_cost': 65536,  # Memory usage in KB (64MB default)
                'parallelism': 1,      # Number of parallel threads
                'hash_len': 32,        # Hash output length in bytes
                'salt_len': 16,        # Salt length in bytes
            },
            'master_key_derivation': 'argon2id',  # Key derivation method
        },
    },
}
```

**Performance vs Security Trade-offs:**
- **Higher `time_cost`**: More secure but slower credential operations
- **Higher `memory_cost`**: More resistant to GPU attacks but uses more RAM
- **Higher `parallelism`**: Faster on multi-core systems but uses more resources

**Recommended Settings:**
- **Default (balanced)**: Good for most deployments
- **High Security**: `time_cost=4`, `memory_cost=131072` (128MB)
- **Low Resource**: `time_cost=2`, `memory_cost=32768` (32MB)

## Advanced Configuration

### SSH Transport Options

Customize SSH connection behavior for legacy or modern devices:

```python
PLUGINS_CONFIG = {
    'netbox_toolkit_plugin': {
        'ssh_options': {
            'disabled_algorithms': {
                'kex': [],  # Key exchange algorithms to disable
            },
            'allowed_kex': [
                'diffie-hellman-group-exchange-sha256',
                'diffie-hellman-group16-sha512',
                # Add more as needed
            ],
        },
    },
}
```

### Netmiko Fallback Configuration

Configure Netmiko behavior when Scrapli connections fail:

```python
PLUGINS_CONFIG = {
    'netbox_toolkit_plugin': {
        'netmiko': {
            'banner_timeout': 20,
            'auth_timeout': 20,
            'global_delay_factor': 1,
            'fast_cli': False,  # Set True for faster connections on modern devices
        },
    },
}
```

### Connection Timeouts

While not directly configurable via PLUGINS_CONFIG, the plugin has intelligent timeout defaults:
- **Default timeouts**: 15-30 seconds (suitable for most devices)
- **Device-specific overrides**: Automatically applied for Catalyst and Nexus devices
- **Fast test mode**: 8-second quick tests before full connection attempts

## Complete Configuration Example

```python
PLUGINS_CONFIG = {
    'netbox_toolkit_plugin': {
        # Security (pepper via environment variable recommended)
        'security': {
            'argon2': {
                'time_cost': 3,
                'memory_cost': 65536,
            },
        },
        # Rate limiting
        'rate_limiting_enabled': True,
        'device_command_limit': 10,
        'time_window_minutes': 5,
        'bypass_users': ['admin'],
        'bypass_groups': ['Network Administrators'],
        # Logging
        'debug_logging': False,
        # Advanced SSH options
        'ssh_options': {
            'allowed_kex': [
                'diffie-hellman-group-exchange-sha256',
                'diffie-hellman-group16-sha512',
            ],
        },
        # Netmiko fallback
        'netmiko': {
            'banner_timeout': 20,
            'fast_cli': False,
        },
    },
}
```




## Quick Reference

| Setting | Default | Description |
|---------|---------|-------------|
| `rate_limiting_enabled` | `True` | Enable/disable rate limiting |
| `device_command_limit` | `10` | Max successful commands per device per time window |
| `time_window_minutes` | `5` | Time window for rate limiting in minutes |
| `bypass_users` | `[]` | List of usernames that bypass rate limiting |
| `bypass_groups` | `[]` | List of group names that bypass rate limiting |
| `debug_logging` | `False` | Enable detailed debug logging |

## Next Steps

After plugin installation and configuration:

1. **Set Up Permissoins**: [Permissions Setup Guide](permissions-creation.md)
2. **Create Commands**: [Command Creation](command-creation.md)

### Common Configuration Issues

#### Plugin Not Loading
- **Symptom**: "Toolkit" tab missing from device pages
- **Check**: Verify `'netbox_toolkit_plugin'` is in the `PLUGINS` list (exact spelling)
- **Solution**: Restart NetBox services after configuration changes

#### Rate Limiting Not Working
- **Symptom**: Users can execute unlimited commands
- **Check**: Verify user is not in `bypass_users` or member of `bypass_groups`
- **Debug**: Enable `debug_logging` to see rate limiting decisions


