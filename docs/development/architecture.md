# Architecture Overview

## Typical Data Flow

A typical command execution flow:

1. User selects a device and command in the web interface
2. View calls the command service to execute the command
3. Service creates a connector via the factory
4. Connector establishes connection to the device
5. Command is executed and results are returned
6. Service logs the execution and processes the results
7. View renders the results to the user

This architecture ensures that each component has a single responsibility, making the code easier to maintain and extend.

## Key Design Patterns
### Factory Pattern
`ConnectorFactory` creates platform-specific connectors:
```python
connector = ConnectorFactory.create_connector(device.platform.slug)
```

### Service Layer Pattern
Business logic isolated in dedicated services:

- `CommandExecutionService` - Command execution with retry logic
- `DeviceService` - Device validation and info
- `RateLimitingService` - Command rate limiting

### Platform-Based Architecture
Commands are tied to NetBox platforms, not device types:
```python
command.platform = device.platform  # 'cisco_ios', 'cisco_nxos', etc.
```


## Error Handling Strategy

### Custom Exception Hierarchy
- `DeviceConnectionError` - Connection failures
- `CommandExecutionError` - Command execution issues  
- `UnsupportedPlatformError` - Platform not supported

### Error Recovery
- Automatic retry mechanisms in `CommandExecutionService`
- Socket error handling in connection utilities
- Detailed error logging and user feedback

## Tech Stack

- **Scrapli/Scrapli-Community** - Primary network device connections
- **Netmiko** - SSH fallback
- **NetBox Platform Model** - Command-platform associations
- **Tabler CSS** - UI framework (NetBox standard)


The error handling architecture provides:

1. **Hierarchical Exceptions**: Custom exceptions for different error categories
2. **Contextual Error Messages**: Errors include guidance based on the specific problem
3. **Graceful Degradation**: Services handle errors and provide useful feedback
4. **Recovery Mechanisms**: Automatic retry with exponential backoff for transient issues

