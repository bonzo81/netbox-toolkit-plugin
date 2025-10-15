# NetBox Toolkit Plugin

 The NetBox Toolkit plugin allows you to run command execution directly from NetBox device pages or via the API. Features command variables, command history, encrypted credential storage with token authentication for API, and comprehensive logging options.

> ⚠️ **EARLY DEVELOPMENT WARNING** ⚠️
> This plugin is in very early development and not recommended for production use. There will be bugs and possible incomplete functionality. Use at your own risk! If you do, give some feedback in [Discussions](https://github.com/bonzo81/netbox-toolkit-plugin/discussions)


### 📋 Feature Overview

- **🔧 Command Creation**: Define platform-specific commands (show/config types) with variables
- **⚡ Command Execution**: Run commands from device pages via "Toolkit" tab or REST API
- **📄 Raw Output**: View complete, unfiltered command responses
- **🔍 Parsed Output**: Automatic JSON parsing using textFSM templates
- **📊 Command Logs**: Complete execution history with timestamps
- **🔐 Secure Credentials**: Encrypted storage with credential tokens via API, or on-the-fly entry in the GUI (no storage required)
- **📊 Statistics Dashboard**: Execution analytics, success rates, and performance metrics
- **🚀 Bulk Operations**: Execute multiple commands across multiple devices via API
- **🐛 Debug Logging**: Optional detailed logging for troubleshooting


### Built with:

- **Scrapli**: Primary network device connection library (SSH/Telnet/NETCONF)
- **Scrapli Community**: Extended platform support for network devices
- **Netmiko**: Fallback SSH client for enhanced device compatibility
- **TextFSM**: Structured data parsing for command outputs

### Security Architecture:

- **Credential Token System**: Secure API execution using credential tokens (no password transmission)
- **Fernet Encryption**: AES-128 CBC + HMAC-SHA256 for credential encryption
- **Argon2id**: Secure key derivation and token hashing with pepper-based authentication
- **Encrypted Storage**: Device credentials encrypted with unique keys per set
- **User Isolation**: Credential tokens bound to specific users
- **No Credential Transmission**: Passwords never sent in API calls
- **Secure Audit Trail**: Operations logged with sanitized data (credentials excluded from change logs)

### 🛠️ Developed With:

[![VS Code](https://img.shields.io/badge/VS_Code-007ACC?style=for-the-badge&logo=visual-studio-code&logoColor=white)](https://code.visualstudio.com/)
[![Dev Containers](https://img.shields.io/badge/Dev_Containers-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://containers.dev/)
[![GitHub Copilot](https://img.shields.io/badge/GitHub_Copilot-000000?style=for-the-badge&logo=github&logoColor=white)](https://github.com/features/copilot)
[![Roo Code](https://img.shields.io/badge/Roo_Code-FF6B6B?style=for-the-badge&logo=visualstudiocode&logoColor=white)](https://github.com/RooVetGit/Roo-Code)


## 📚 Essential Guides

#### 🚀 Getting Started
- [📦 Plugin Installation](./docs/user/plugin-installation.md) - Install the plugin in your NetBox environment
- [🔄 Plugin Upgrade](./docs/user/plugin-upgrade.md) - Upgrade to newer versions
- [⚙️ Plugin Configuration](./docs/user/plugin-configuration.md) - Configure plugin settings and options
- [🔐 Permissions Creation](./docs/user/permissions-creation.md) - Set up user access and permissions
- [📋 Command Creation](./docs/user/command-creation.md) - Create platform-specific commands with variables
- [🔑 Device Credentials](./docs/user/device-credentials.md) - Secure credential storage and token management
- [📝 Logging Guide](./docs/user/logging.md) - Enable logging for troubleshooting

#### 🔌 API Integration
- [📖 API Overview](./docs/api/index.md) - REST API capabilities and features
- [🔑 Authentication & Permissions](./docs/api/auth.md) - API authentication with credential tokens
- [⚡ Commands API](./docs/api/commands.md) - Command execution and management
- [📊 Command Logs API](./docs/api/command-logs.md) - Access execution history and logs
- [� Error Handling](./docs/api/errors.md) - API error responses and troubleshooting
- [🔄 API Workflows](./docs/api/workflows.md) - Common API usage patterns
- [🤖 Automation Examples](./docs/api/automation-examples.md) - Scripts and automation scenarios

#### 📋 Configuration Examples
- [📝 Permission Examples](./docs/user/permission-examples.md) - Example permission configurations
- [⚖️ GUI vs API Comparison](./docs/user/gui-vs-api.md) - Feature comparison between web interface and API

#### 👨‍💻 Development
- [🏗️ Developer Guide](./docs/development/index.md) - Complete overview for contributors
- [🔧 Development Setup](./docs/development/setup.md) - Set up your development environment

## Demo
*Demo from older plugin version*

![Plugin Demo](docs/img/demo1.gif)

### Quick Start

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

**Initial Setup (Required):**

1. **[Set up permissions](./docs/user/permissions-creation.md)** - Grant users access to execute commands
2. **[Create commands](./docs/user/command-creation.md)** - Define platform-specific commands (e.g., "show version")


> **Note**: Using credential token allows for secure command execution via API without transmitting passwords! 🔒

3. **[Add credentials](./docs/user/device-credentials.md) (Optional for GUI)** - Create credential sets or enter on-the-fly per command (GUI) / Create credential set and copy token (API)

**Using the GUI:**

1. Navigate to any device page → **"Toolkit"** tab
2. Select a command, enter variables (if any), choose credentials (or enter on-the-fly), and execute
3. View results with raw or parsed output

**Using the API:**

Execute commands programmatically:

```bash
curl -X POST "https://netbox.example.com/api/plugins/toolkit/commands/17/execute/" \
  -H "Authorization: Token <your-netbox-api-token>" \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": 1,
    "credential_token": "<your-credential-token>"
  }'
```



📖 **Full installation guide:** [Plugin Installation](./docs/user/plugin-installation.md)

## Contributing

**🚀 Want to Contribute?** Get started quickly with the **[Dev Container setup](./docs/development/setup.md#quick-start-with-dev-container-recommended)** or use the [Contributor Guide](./docs/development/index.md) for a complete overview of the codebase.


## Completed Features:
- ✅ API returns both parsed and raw command output
- ✅ Command variables with NetBox attribute integration (interfaces, VLANs, IPs)
- ✅ Statistics dashboard with execution analytics
- ✅ On-the-fly credential entry (no storage required)
- ✅ Argon2id security with pepper-based authentication
- ✅ Search functionality across commands and logs
- ✅ Platform normalization for connector selection
- ✅ CSV export for parsed command outputs

## Future Features:
- ⬜ Diff/Comparison Tools - Compare command outputs over time or between devices
- ⬜ Enhanced Variable Types - Support for more NetBox objects (sites, tenants, device roles, cables, etc.)

