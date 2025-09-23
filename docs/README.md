# NetBox Toolkit ## 📚 Essential Guides

| Setup | Configuration | Usage |
|---|---|---|
| [📦 Installation](./user/installation.md) | [⚙️ Configuration](./user/configuration.md) | [📋 Command Creation](./user/command-creation.md) |
| [🔐 Permissions Setup](./user/permissions-setup-guide.md) | [🔑 Device Credential Sets](./user/getting-started.md#device-credential-sets) | [📝 Permission Examples](./user/permission-examples.md) |
| [🔌 API Authentication](./api/auth.md) | [⚡ Commands API](./api/commands.md) | [🐛 Debug Logging](./user/debug-logging.md) |

Execute network commands securely from NetBox with encrypted credential storage, dual-token authentication, and comprehensive API automation.

## 🚀 What Does This Plugin Do?

### 📋 Feature Overview
- **🔧 Command Creation**: Define platform-specific commands (show/config types) with variables
- **🔐 Secure Credential Storage**: Encrypted device credentials with credential tokens
- **🔑 Dual-Token Security**: NetBox API tokens + credential tokens for enhanced security
- **⚡ Command Execution**: Run commands from device pages via "Toolkit" tab or REST API
- **📄 Raw Output**: View complete, unfiltered command responses
- **🔍 Parsed Output**: Automatic JSON parsing using textFSM templates
- **📊 Command Logs**: Complete execution history with timestamps
- **🚀 Bulk Operations**: Execute multiple commands across multiple devices via API
- **� Debug Logging**: Optional detailed logging for troubleshooting

## 📚 Essential Guides

| Setup | Configuration | Usage |
|---|---|---|
| [📦 Installation](./user/installation.md) | [⚙️ Configuration](./user/configuration.md) | [📋 Command Creation](./user/command-creation.md) |
| [🔐 Permissions Setup](./user/permissions-setup-guide.md) | [� Permission Examples](./user/permission-examples.md) | [🐛 Debug Logging](./user/debug-logging.md) |

## 🚀 Workflow Examples

| Web Interface | API Integration | Advanced Scenarios |
|---|---|---|
| [🎯 Interactive Workflows](./user/workflow-examples.md#web-interface-workflows) | [🔧 API Workflows](./api/workflows.md) | [🏢 Enterprise Automation](./user/workflow-examples.md#api-exclusive-advanced-workflow) |
| Device troubleshooting | Credential token setup | Compliance automation |
| Command development | Bulk operations | Network monitoring |
| Secure credential storage | System integration | Multi-user environments |


## ⚡ Toolkit Setup Steps

Follow these steps to get the NetBox Toolkit Plugin running in your environment.

First activate your NetBox virtual environment and install the plugin:

```bash
source /opt/netbox/venv/bin/activate
```

### 1. **Install the Plugin** - [Detailed Installation Guide](./user/installation.md)
```bash
pip install netbox-toolkit-plugin
```



### 2. **Enable in NetBox** - [Configuration Details](./user/configuration.md)
Add `'netbox_toolkit'` to `PLUGINS` in your NetBox configuration



### 3. **Run Database Migration**
```bash
python manage.py migrate netbox_toolkit
```

### 4. **Configure Plugin Settings** - [Configuration Options](./user/configuration.md)
Add basic settings to `PLUGINS_CONFIG` in your NetBox configuration

### 5. **Set Up Permissions** - [Permissions Setup Guide](./user/permissions-setup-guide.md)
Create either 'show' or 'config' command execution permissions to assign to users or groups

### 6. **Create Device Credential Sets** - [Getting Started Guide](./user/getting-started.md#device-credential-sets)
Set up secure, encrypted credential storage with credential tokens for API access

### 7. **Create Commands** - [Command Creation Guide](./user/command-creation.md)
Define platform-specific commands with variables through the NetBox admin interface

### 8. **Start Using**
- **Web Interface**: Visit any device page → "Toolkit" tab → Execute commands
- **REST API**: Use dual-token authentication for secure automation - [API Guide](./api/auth.md)

## 🌐 Platform Support

The plugin uses **Scrapli** as the primary connection library with **Netmiko** as a fallback, providing robust support for various network device platforms:

### Primary Connection Engine: Scrapli
Scrapli provides fast, modern SSH connectivity with structured output parsing capabilities:

- **Cisco IOS/IOS-XE** (`cisco_ios`) - Traditional Cisco platforms with TextFSM parsing
- **Cisco NX-OS** (`cisco_nxos`) - Data center switching with enhanced JSON output support
- **Cisco IOS-XR** (`cisco_iosxr`) - Service provider routing platforms
- **Juniper Junos** (`juniper_junos`) - Juniper devices with XML/JSON output parsing
- **Arista EOS** (`arista_eos`) - Arista switches with native JSON API support

### Fallback Connection: Netmiko
When Scrapli encounters connection issues, the plugin automatically falls back to Netmiko for broader device compatibility:

- **Extended Platform Support** - Covers additional vendor platforms and older device models
- **Legacy Device Support** - Better compatibility with older firmware versions
- **SSH Troubleshooting** - Alternative SSH implementation for problematic connections

### Key Benefits
- **Automatic Fallback**: Seamless switching between connection methods
- **TextFSM Integration**: Structured data parsing for show commands
- **JSON Output**: Native support for modern network OS JSON responses
- **Connection Resilience**: Multiple connection strategies ensure reliability


### Platform Selection
When creating commands, select the appropriate platform slug to ensure:

- Correct command syntax validation
- Optimal connection method selection
- Proper output parsing (TextFSM templates, JSON, etc.)
- Platform-specific error handling

## 📊 Command Logs
Complete execution history tracking:

- **Timestamp** - When command was executed
- **User** - Who executed the command
- **Device** - Target device information
- **Command** - Exact command executed
- **Status** - Success/failure with error details
- **Duration** - Execution time

## � Security Features

### Dual-Token Authentication System
- **NetBox API Token**: Standard user authentication
- **Credential Token**: References encrypted device credentials
- **User Isolation**: Credential tokens bound to specific users
- **No Password Transmission**: Credentials never sent in API calls

### Encrypted Credential Storage
- **Fernet Encryption**: Industry-standard symmetric encryption
- **Unique Key Derivation**: Each credential set has unique encryption keys
- **No Key Storage**: Keys derived deterministically from master secret
- **Secure Token Generation**: URL-safe random credential tokens

### Audit & Compliance
- **Complete Audit Trail**: All executions logged with user attribution
- **Permission Integration**: Leverages NetBox's ObjectPermission system
- **Granular Access Control**: Separate permissions for show vs config commands
- **Cross-User Protection**: Users cannot access each other's credentials

## �🐛 Debug Logging
Optional detailed logging for troubleshooting:

- **Connection details** - SSH handshake and authentication
- **Command flow** - Step-by-step execution process
- **Error diagnostics** - Detailed failure messages

## 👨‍💻 For Developers

**Start Here**: [Contributor Guide](./development/contributing.md) - Fast navigation for developers ⭐

### Core Documentation
- [Architecture Overview](./development/architecture.md) - System design and patterns
- [Module Structure](./development/module-structure.md) - Code organization and key classes
- [Development Setup](./development/setup.md) - Environment setup and workflows (includes develop branch)
