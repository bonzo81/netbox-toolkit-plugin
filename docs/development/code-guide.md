# NetBox Toolkit Plugin - Code Guide

Quick navigation guide for developers working on the NetBox Toolkit Plugin codebase.

## 📁 Key Files & Classes

### Core Models (`netbox_toolkit/models.py`)
- **`Command`** - Platform-based commands (show/config types)
- **`CommandLog`** - Execution history with error detection

### Service Layer (`netbox_toolkit/services/`)
- **`CommandExecutionService`** - Main command execution logic
- **`DeviceService`** - Device validation and connection info
- **`RateLimitingService`** - Prevents command flooding

### Connector Framework (`netbox_toolkit/connectors/`)
- **`BaseDeviceConnector`** - Abstract interface for all connectors
- **`ScrapliConnector`** - Scrapli-based implementation (primary)
- **`ConnectorFactory`** - Creates platform-specific connectors

### Views (`netbox_toolkit/views.py`)
- **`DeviceToolkitView`** - Custom "Toolkit" tab on device pages
- **`CommandListView`** - Command management interface


## 📦 Dependencies

### Primary Libraries
- **Scrapli** - Network device connections (SSH/Telnet/NETCONF)
- **Scrapli-Community** - Extended platform support
- **Netmiko** - SSH fallback

### NetBox Integration
- Uses NetBox's `Platform` model (not `DeviceType`)
- Leverages `ObjectPermission` for access control
- Integrates with NetBox's tab system via `ViewTab`

## 🔧 Configuration

Central config in `config.py`:
- Connection timeouts
- SSH options
- Debug settings
- Rate limiting parameters
