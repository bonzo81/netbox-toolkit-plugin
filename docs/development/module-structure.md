# Module Structure

## Quick Reference

**Key Classes by Module:**

- **`models.py`**: `Command`, `CommandLog` 
- **`views.py`**: `DeviceToolkitView`, `CommandListView`
- **`services/command_service.py`**: `CommandExecutionService`
- **`services/device_service.py`**: `DeviceService`
- **`services/rate_limiting_service.py`**: `RateLimitingService`
- **`connectors/factory.py`**: `ConnectorFactory`
- **`connectors/scrapli_connector.py`**: `ScrapliConnector`
- **`connectors/netmiko_connector.py`**: `NetmikoConnector`

## Directory Structure

```
netbox_toolkit_plugin/
├── __init__.py             # Plugin initialization
├── admin.py                # Django admin interface definitions
├── config.py               # Plugin configuration settings
├── exceptions.py           # Custom exception classes
├── filtersets.py           # Filter definitions for views
├── forms.py                # Django form definitions
├── models.py               # Django data models
├── navigation.py           # NetBox navigation integration
├── tables.py               # NetBox table definitions
├── urls.py                 # URL routing definitions
├── views.py                # Django view implementations
├── api/                    # REST API implementation
│   ├── __init__.py
│   ├── serializers.py      # API serializers
│   ├── urls.py             # API URL routing
│   └── views.py            # API views
├── connectors/             # Device connection framework
│   ├── __init__.py
│   ├── base.py             # Abstract connector interfaces
│   ├── factory.py          # Connector factory implementation
│   ├── netmiko_connector.py # Netmiko-based connector implementation
│   └── scrapli_connector.py # Scrapli-based connector implementation
├── migrations/             # Django database migrations
├── services/               # Business logic services
│   ├── __init__.py
│   ├── command_service.py  # Command execution service
│   ├── device_service.py   # Device management service
│   └── rate_limiting_service.py # Rate limiting service
├── static/                 # Static assets (CSS, JavaScript)
│   └── netbox_toolkit_plugin/
│       ├── css/
│       │   └── toolkit.css
│       └── js/
│           └── toolkit.js
├── templates/              # Django HTML templates
│   └── netbox_toolkit_plugin/
│       ├── command.html
│       ├── command_edit.html
│       ├── command_list.html
│       ├── commandlog.html
│       ├── commandlog_list.html
│       └── device_toolkit.html
└── utils/                  # Utility functions
    ├── __init__.py
    ├── connection.py       # Connection utilities
    ├── error_parser.py     # Network error parsing utilities
    ├── logging.py          # Logging utilities
    └── network.py          # Network utilities
```

## Core Modules

### Plugin Core

- **models.py**: `Command` (platform-based commands), `CommandLog` (execution history)
- **views.py**: `DeviceToolkitView` (device tab), view classes for command management
- **config.py**: `ToolkitSettings` class with connection timeouts and SSH settings
- **exceptions.py**: `DeviceConnectionError`, `CommandExecutionError`, `UnsupportedPlatformError`

### Service Layer (`services/`)

- **command_service.py**: `CommandExecutionService` - Core command execution logic
- **device_service.py**: `DeviceService` - Device validation and connection info
- **rate_limiting_service.py**: `RateLimitingService` - Command rate limiting

### Connector Framework (`connectors/`)

- **base.py**: `BaseDeviceConnector` - Abstract interface, `CommandResult` data class
- **factory.py**: `ConnectorFactory` - Platform-based connector creation
- **scrapli_connector.py**: `ScrapliConnector` - Scrapli library implementation
- **netmiko_connector.py**: `NetmikoConnector` - Netmiko library implementation

### API Layer (`api/`)

- **views.py**: `CommandViewSet` with `execute_command` action - REST API for command execution
- **serializers.py**: `CommandSerializer`, `CommandLogSerializer` - API data serialization

