# NetBox Toolkit Plugin

## 📚 Essential Guides

| Setup | Configuration | Usage |
|---|---|---|
| [📦 Installation](./user/plugin-installation.md) | [⚙️ Configuration](./user/plugin-configuration.md) | [📋 Command Creation](./user/command-creation.md) |
| [🔐 Permissions Setup](./user/permissions-creation.md) | [🔑 Device Credential Sets](./user/device-credentials.md) | [📝 Permission Examples](./user/permission-examples.md) |
| [🔌 API Authentication](./api/auth.md) | [⚡ Commands API](./api/commands.md) | [� Logging Guide](./user/logging.md) |

Execute network commands securely from NetBox with encrypted credential storage, secure credential tokens, and comprehensive API automation.

## 🚀 What Does This Plugin Do?

### 📋 Core Features
- **🔧 Command Management**: Define platform-specific network commands with variables
- **🔐 Secure Credentials**: Encrypted credential storage with token-based access
- **🔑 Secure Credentials**: NetBox API authentication + encrypted credential tokens for device access
- **⚡ Command Execution**: Run commands from device pages or via REST API
- **📄 Raw & Parsed Output**: View complete responses with automatic structured parsing
- **📊 Execution Logs**: Complete command history with timestamps and user tracking
- **🚀 Bulk Operations**: Execute multiple commands across multiple devices via API
- **🛡️ Access Control**: Granular permissions for show vs configuration commands

## ⚡ Toolkit Setup Steps

Follow these steps to get the NetBox Toolkit Plugin running in your environment.

First activate your NetBox virtual environment and install the plugin:

```bash
source /opt/netbox/venv/bin/activate
```

### 1. **Install the Plugin** - [Detailed Installation Guide](./user/plugin-installation.md)
```bash
pip install netbox-toolkit-plugin
```



### 2. **Enable in NetBox** - [Configuration Details](./user/plugin-configuration.md)
Add `'netbox_toolkit'` to `PLUGINS` in your NetBox configuration



### 3. **Run Database Migration**
```bash
python manage.py migrate netbox_toolkit
```

### 4. **Configure Plugin Settings** - [Configuration Options](./user/plugin-configuration.md)
Add basic settings to `PLUGINS_CONFIG` in your NetBox configuration

### 5. **Set Up Permissions** - [Permissions Setup Guide](./user/permissions-creation.md)
Create either 'show' or 'config' command execution permissions to assign to users or groups

### 6. **Create Device Credential Sets** - [Device Credentials Guide](./user/device-credentials.md)
Set up secure, encrypted credential storage with credential tokens for API access

### 7. **Execute Commands** - [Command Creation Guide](./user/command-creation.md)
Define platform-specific commands with variables through the NetBox admin interface

### 8. **Start Using**
- **Web Interface**: Visit any device page → "Toolkit" tab → Execute commands
- **REST API**: Use NetBox authentication with credential tokens for secure automation - [API Guide](./api/auth.md)

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



