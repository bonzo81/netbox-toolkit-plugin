# Installation

This guide covers the basic steps to install the NetBox Toolkit Plugin. For detailed configuration options, see the [Plugin Configuration](./plugin-configuration.md) guide.


## Installation Steps

### 1. **Install the Plugin**

Activate your virtual environment and install:

```bash
source /opt/netbox/venv/bin/activate
pip install netbox-toolkit-plugin
```

### 2. **Enable the Plugin**

Add to your NetBox `configuration.py`:

```python
PLUGINS = [
    'netbox_toolkit_plugin',
]
```

### 3. **Configure Security Pepper (REQUIRED)**

The plugin requires a security pepper for credential encryption. Choose one method:

**Option A: Configuration File (Recommended)**

```bash
# Generate a secure pepper (copy the output)
python3 -c "import secrets; print(secrets.token_urlsafe(48))"
```

Add to `configuration.py`:

```python
PLUGINS_CONFIG = {
    'netbox_toolkit_plugin': {
        'security': {
            'pepper': 'your-generated-pepper-here',  # Paste the generated value
        },
    },
}
```

**Option B: Environment Variable**

```bash
export NETBOX_TOOLKIT_PEPPER="your-generated-pepper-here"
```

> **⚠️ Warning:** Using `export` only sets the variable for the current shell session. It will be lost on system reboot or when the shell closes. For production use with systemd, use Option A (config file) instead.

**Option C: Docker Compose**

```yaml
services:
  netbox:
    environment:
      - NETBOX_TOOLKIT_PEPPER=your-generated-pepper-here
```

> **📖 More Details:** See [Plugin Configuration - Security Pepper](./plugin-configuration.md#security-pepper-required) for detailed setup options, pros/cons, and security best practices.

### 4. **Run Database Migrations**

```bash
cd /opt/netbox/netbox
python3 manage.py migrate netbox_toolkit_plugin
```

### 5. **Collect Static Files**

```bash
python3 manage.py collectstatic --no-input
```

### 6. **Restart NetBox**

```bash
sudo systemctl restart netbox netbox-rq
```


## Configure Optional Settings

The plugin works with default settings, but you can customize:

- **Rate Limiting**: Control command execution frequency
- **Debug Logging**: Enable detailed logs for troubleshooting
- **Advanced Security**: Fine-tune Argon2id parameters

**📖 See [Plugin Configuration](./plugin-configuration.md) for all available options.**

## Next Steps

After successful installation:

1. **[Set Up Permissions](permissions-creation.md)** - Configure user access to plugin features
2. **[Create Commands](command-creation.md)** - Define platform-specific commands
3. **[Add Credentials](device-credentials.md)** - Set up device credentials for command execution

## Troubleshooting

**Plugin tab not appearing?**
- Verify plugin is in `PLUGINS` list
- Check pepper is configured
- Review logs: `sudo journalctl -u netbox -n 50`

**Migration errors?**
- Ensure virtual environment is activated
- Check database connectivity
- See [Plugin Upgrade](plugin-upgrade.md#troubleshooting) for more help

