# NetBox Toolkit Plugin - Copilot Instructions

## Unique Tech Stack
- **Scrapli**: Primary network device connection library (SSH/Telnet/NETCONF)
- **Scrapli-Community**: Extended platform support for network devices
- **Netmiko**: SSH client fallback for device connections
- **Tabler**: CSS framework (NetBox uses Tabler, not Bootstrap)

## Response Format
- Don't create test scripts or test cases unless explicitly requested
- Use Context7 tool for retrieving documentation

## Key Architecture Patterns
- Use `device.platform.slug` for connector selection (not device_type)
- Factory pattern: `ConnectorFactory.create_connector(platform.slug)`
- Service layer: `CommandExecutionService`, `DeviceService`
- NetBox permissions: `ObjectPermission` with `execute_show`/`execute_config` actions

## Plugin-Specific Architecture

### Core Module Structure
```
netbox_toolkit/
├── connectors/         # Device connection abstraction (Scrapli-based)
├── services/          # Business logic (CommandExecutionService, DeviceService)
├── utils/             # Network utilities and error parsing
└── api/               # REST API with command execution endpoints
```

### Key NetBox Integration Points
- `@register_model_view(Device, name='toolkit', path='toolkit')` - Adds "Toolkit" tab to device pages
- `ViewTab(label='Toolkit')` - Custom device tab integration
- `ObjectPermission` - NetBox's permission system for command execution
- URL namespace: `plugins:netbox_toolkit_plugin:*` for all plugin URLs

### Unique Models & Relationships
- **Command**: Platform-based commands (not device-type based)
- **CommandLog**: Execution history with syntax error detection
- Command → Platform (many-to-one) - Uses NetBox's Platform model
- Commands filtered by user permissions: `execute_show`, `execute_config` actions

### Connector Pattern
```python
# Factory pattern for device connections
connector = ConnectorFactory.create_connector(device.platform.slug)
result = connector.execute_command(command, credentials)
```

### Service Layer Pattern
- `CommandExecutionService`: Handles command execution with retry logic
- `DeviceService`: Device validation and connection info
- Syntax error detection for network device responses

### Permission System Integration
```python
def _user_has_action_permission(self, user, obj, action):
    # Uses NetBox's ObjectPermission system
    # Actions: 'execute_show', 'execute_config'
```

### Scrapli Integration Patterns
- Platform-based connector selection (cisco_ios, cisco_nxos, etc.)
- Socket error handling and retry mechanisms
- Connection timeout and transport configuration

### Common Pitfalls to Avoid
- ❌ Don't use device.device_type - use device.platform instead
- ❌ Don't create custom CSS when Tabler classes exist
- ❌ Don't bypass NetBox's permission system
- ❌ Don't hardcode connection parameters - use the config system
- ❌ Don't forget to handle connection timeouts and retries
- ❌ Don't use generic SSH libraries - prefer Scrapli/Netmiko

