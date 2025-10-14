# NetBox Toolkit Plugin

A comprehensive NetBox plugin for secure network device command execution with encrypted credential storage, dual-token authentication, and powerful automation capabilities.

> ⚠️ **EARLY DEVELOPMENT WARNING** ⚠️
> This plugin is in very early development and not recommended for production use. There will be bugs and possible incomplete functionality. Use at your own risk! If you do, give some feedback in [Discussions](https://github.com/bonzo81/netbox-toolkit-plugin/discussions)

Execute network commands on devices directly from NetBox device pages with secure credential management and comprehensive logging.


### 📋 Feature Overview
- **🔧 Command Creation**: Define platform-specific commands (show/config types) with variables
- **🔐 Secure Credential Storage**: Encrypted device credentials with credential tokens
- **🔑 Dual-Token Security**: NetBox API tokens + credential tokens for enhanced security
- **⚡ Command Execution**: Run commands from device pages via "Toolkit" tab or REST API
- **📄 Raw Output**: View complete, unfiltered command responses
- **🔍 Parsed Output**: Automatic JSON parsing using textFSM templates
- **📊 Command Logs**: Complete execution history with timestamps
- **🚀 Bulk Operations**: Execute multiple commands across multiple devices via API
- **🐛 Debug Logging**: Optional detailed logging for troubleshooting


### Built with:
- **Scrapli**: Primary network device connection library (SSH/Telnet/NETCONF)
- **Scrapli Community**: Extended platform support for network devices
- **Netmiko**: Fallback SSH client for enhanced device compatibility
- **TextFSM**: Structured data parsing for command outputs
- **Fernet Encryption**: Secure credential storage with unique key derivation

### Security Architecture:
- **Dual-Token Authentication**: NetBox API tokens + credential tokens
- **Encrypted Storage**: Device credentials encrypted with unique keys per set
- **User Isolation**: Credential tokens bound to specific users
- **No Credential Transmission**: Passwords never sent in API calls
- **Audit Trail**: All operations logged with proper user attribution

### Created with:
- VSCode + Dev Containers
- Copilot
- RooCode

>   This project is a work in progress and in early development. It is not recommended for production use. Feedback and contributions are welcome!

## 📚 Essential Guides

#### 🚀 Getting Started
- [📦 Plugin Installation](./docs/user/plugin-installation.md) - Install the plugin in your NetBox environment
- [⚙️ Plugin Configuration](./docs/user/plugin-configuration.md) - Configure plugin settings and options
- [🔐 Permissions Creation](./docs/user/permissions-creation.md) - Set up user access and permissions
- [📋 Command Creation](./docs/user/command-creation.md) - Create platform-specific commands with variables
- [🔑 Device Credentials](./docs/user/device-credentials.md) - Secure credential storage and token management

#### 📋 Advanced Configuration
- [📝 Permission Examples](./docs/user/permission-examples.md) - Example permission configurations
- [🔐 Legacy Permissions](./docs/user/permissions-creation.md) - Legacy permission setup guide

#### 🔌 API Integration
- [📖 API Overview](./docs/api/overview.md) - REST API capabilities and features
- [🔑 Authentication & Permissions](./docs/api/auth.md) - Dual-token authentication system
- [⚡ Commands API](./docs/api/commands.md) - Command execution and bulk operations

#### 🔧 Troubleshooting
- [� Logging Guide](./docs/user/logging.md) - Enable logging for troubleshooting

## Demo

![Plugin Demo](docs/img/demo1.gif)

### Quick Start Example

```bash
# 1. Create Device Credential Set in NetBox web interface
# 2. Copy the generated credential token
# 3. Execute commands via API:

curl -X POST "https://netbox.example.com/api/plugins/toolkit/commands/17/execute/" \
  -H "Authorization: Token <your-netbox-api-token>" \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": 1,
    "credential_token": "<your-credential-token>"
  }'
```

**Result**: Secure command execution without transmitting passwords! 🔒

## Contributing

**🚀 Want to Contribute?** Get started quickly with the **[Dev Container setup](./docs/development/setup.md#quick-start-with-dev-container-recommended)** or use the [Contributor Guide](./docs/development/index.md) for a complete overview of the codebase.


## Future ideas:
- Enhance API to allow execution of commands and return either parsed or raw data.
- Enable variable use in the command creation and execution, based on device attributes.

