# Technical Stack & Architecture

Understanding these technical details helps guide contribution decisions and ensures consistency with the project's design.

## 🏗️ Architecture Principles

### Core Design Patterns

✅ **Platform-Based Commands**: All commands are tied to NetBox platforms (see `netbox_toolkit_plugin/models.py`)

✅ **Service Layer Architecture**: Business logic isolated in dedicated service classes (see `services/` directory)

✅ **Connector Abstraction**: Uniform interface for all device connections (see `connectors/` directory)

✅ **Permission Integration**: Leverages NetBox's ObjectPermission system for access control

✅ **Secure Credentials**: NetBox API authentication + encrypted credential tokens for enhanced security

## 🔧 Technical Stack

### Primary Network Libraries

- **[Scrapli](https://github.com/carlmontanari/scrapli)**: Primary connection library (SSH/Telnet/NETCONF)
- **[Scrapli-Community](https://github.com/scrapli/scrapli_community)**: Extended platform support
- **[Netmiko](https://github.com/ktbyers/netmiko)**: SSH fallback for legacy or problematic devices
- **[TextFSM](https://github.com/google/textfsm)**: Structured output parsing

### NetBox Integration Points

- **Platform Model**: Commands are bound to NetBox platforms, not device types
- **ObjectPermission System**: Granular access control using NetBox's permission framework
- **ViewTab System**: Custom tabs integrated into NetBox device pages
- **Plugin Configuration**: Standard NetBox plugin configuration patterns