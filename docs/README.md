# NetBox Toolkit Plugin

 The NetBox Toolkit plugin allows you to run command execution directly from NetBox device pages or via the API. Features command variables, command history, encrypted credential storage with token authentication for API, and comprehensive logging options.

> ⚠️ **EARLY DEVELOPMENT WARNING** ⚠️
> This plugin is in very early development and not recommended for production use. There will be bugs and possible incomplete functionality. Use at your own risk! If you do, give some feedback in [Discussions](https://github.com/bonzo81/netbox-toolkit-plugin/discussions)


### 📋 Core Features

- **🔧 Command Creation**: Define platform-specific commands (show/config types) with variables

- **⚡ Command Execution**: Run commands from device pages via "Toolkit" tab or REST API
- **📄 Raw Output**: View complete, unfiltered command responses
- **🔍 Parsed Output**: Automatic JSON parsing using textFSM templates
- **📊 Command Logs**: Complete execution history with timestamps
- **🔐 Secure Credentials**: Encrypted storage with credential tokens via API, or on-the-fly entry in the GUI (no storage required)
- **📊 Statistics Dashboard**: Execution analytics, success rates, and performance metrics
- **🚀 Bulk Operations**: Execute multiple commands across multiple devices via API
- **🐛 Debug Logging**: Optional detailed logging for troubleshooting


## 📚 Essential Guides

### 🚀 Getting Started
- [📦 Plugin Installation](./user/plugin-installation.md) - Install the plugin in your NetBox environment
- [🔄 Plugin Upgrade](./user/plugin-upgrade.md) - Upgrade to newer versions
- [⚙️ Plugin Configuration](./user/plugin-configuration.md) - Configure plugin settings and security options
- [🔐 Permissions Creation](./user/permissions-creation.md) - Set up user access and permissions
- [📋 Command Creation](./user/command-creation.md) - Create platform-specific commands with variables
- [🔑 Device Credentials](./user/device-credentials.md) - Secure credential storage and token management
- [📝 Logging Guide](./user/logging.md) - Enable logging for troubleshooting

### 🔌 API Integration
- [📖 API Overview](./api/index.md) - REST API capabilities and features
- [🔑 Authentication & Permissions](./api/auth.md) - API authentication with credential tokens
- [⚡ Commands API](./api/commands.md) - Command execution and management
- [📊 Command Logs API](./api/command-logs.md) - Access execution history and logs
- [🛡️ Error Handling](./api/errors.md) - API error responses and troubleshooting
- [🔄 API Workflows](./api/workflows.md) - Common API usage patterns
- [🤖 Automation Examples](./api/automation-examples.md) - Scripts and automation scenarios

### 📋 Configuration Examples
- [📝 Permission Examples](./user/permission-examples.md) - Example permission configurations
- [⚖️ GUI vs API Comparison](./user/gui-vs-api.md) - Feature comparison between web interface and API

### 👨‍💻 Development
- [🏗️ Developer Guide](./development/index.md) - Complete overview for contributors
- [🔧 Development Setup](./development/setup.md) - Set up your development environment



### Security Architecture
- **Credential Token System**: Secure API execution using credential tokens (no password transmission)
- **Fernet Encryption**: AES-128 CBC + HMAC-SHA256 for credential encryption
- **Argon2id**: Secure key derivation and token hashing with pepper-based authentication
- **Encrypted Storage**: Device credentials encrypted with unique keys per set
- **User Isolation**: Credential tokens bound to specific users
- **No Credential Transmission**: Passwords never sent in API calls
- **Secure Audit Trail**: Operations logged with sanitized data (credentials excluded from change logs)

### Built With
- **Scrapli**: Primary network device connection library (SSH/Telnet/NETCONF)
- **Scrapli Community**: Extended platform support for network devices
- **Netmiko**: Fallback SSH client for enhanced device compatibility
- **TextFSM**: Structured data parsing for command outputs

See [Platform Support](./platform-support.md) for detailed information on supported network devices and connection methods.

### Minimal Install

**Installation:**

```bash
# 1. Install the plugin
pip install netbox-toolkit-plugin

# 2. Add to NetBox configuration.py
PLUGINS = ['netbox_toolkit_plugin']

# 3. Configure security pepper (REQUIRED)
python3 -c "import secrets; print(secrets.token_urlsafe(48))"  # Generate pepper

PLUGINS_CONFIG = {
    'netbox_toolkit_plugin': {
        'security': {
            'pepper': 'your-generated-pepper-here',
        },
    },
}

# 4. Run migrations and restart
python3 manage.py migrate netbox_toolkit_plugin
python3 manage.py collectstatic --no-input
sudo systemctl restart netbox netbox-rq
```

📖 **Full installation guide:** [Plugin Installation](./user/plugin-installation.md)




