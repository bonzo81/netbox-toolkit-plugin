# API Reference

The NetBox Toolkit Plugin provides a comprehensive REST API for network device command execution and management. The API offers **complete feature parity** with the web interface and includes **additional capabilities** not available through the GUI, making it ideal for automation, integration, and advanced workflows.

## Key Advantages of the API

🚀 **Enhanced Capabilities Beyond GUI:**
- **Bulk Operations**: Execute multiple commands across multiple devices simultaneously
- **Advanced Statistics**: Comprehensive execution analytics and reporting
- **Flexible Export**: Multiple formats with advanced filtering options
- **Programmatic Validation**: Pre-validate variables without execution
- **Integration Ready**: Perfect for automation workflows and third-party integrations

✅ **Complete Feature Parity:**
Every feature available in the web interface is fully accessible via API, ensuring consistent functionality across all access methods.

## Quick Start

### Authentication

All API requests require authentication using NetBox's token system:

```bash
curl -H "Authorization: Token YOUR_TOKEN_HERE" \
     -H "Content-Type: application/json" \
     https://netbox.example.com/api/plugins/toolkit/commands/
```

### Base URL

All API endpoints are prefixed with:
```
/api/plugins/toolkit/
```

## Available Resources

Each API resource has its own dedicated documentation page:

### [Commands API](commands.md)
- **Purpose**: Manage network commands and execute them on devices
- **Endpoints**: `/commands/`
- **Key Features**:
  - Complete CRUD operations for command management
  - Single and bulk command execution
  - Variable validation and dynamic choices
  - Advanced filtering and search capabilities
  - **API Exclusive**: Bulk execution across multiple devices

### [Command Logs API](command-logs.md)
- **Purpose**: Track command execution history and results
- **Endpoints**: `/command-logs/`
- **Key Features**:
  - Comprehensive execution history tracking
  - **API Exclusive**: Advanced statistics and analytics
  - Flexible export capabilities (CSV/JSON with date filtering)
  - Performance monitoring and error analysis

### [Authentication & Permissions](auth.md)
- **Purpose**: Security and access control
- **Key Features**: Token authentication, object permissions, action permissions

### [Error Handling](errors.md)
- **Purpose**: Error codes and troubleshooting
- **Key Features**: Error structure, common errors, resolution strategies

### [Feature Comparison](feature-comparison.md)
- **Purpose**: Comprehensive comparison between API and Web Interface
- **Key Features**: Feature matrix, use case guidance, migration strategies

### [API Workflows](workflows.md)
- **Purpose**: Focused API workflow examples and integration patterns
- **Key Features**: Bulk operations, automation examples, integration code samples

### [Complete Workflow Guide](../user/workflow-examples.md)
- **Purpose**: Comprehensive workflow examples for both GUI and API usage
- **Key Features**: Real-world scenarios, step-by-step guides, best practices

## Common Patterns

### Pagination
All list endpoints support pagination:
```bash
GET /api/plugins/toolkit/commands/?limit=50&offset=100
```

### Filtering
Extensive filtering is available on most endpoints:
```bash
GET /api/plugins/toolkit/commands/?platform_slug=cisco_ios&command_type=show
```

### Sorting
Results can be sorted using the `ordering` parameter:
```bash
GET /api/plugins/toolkit/command-logs/?ordering=-execution_time
```

## Interactive Documentation

- **Swagger UI**: `/api/docs/`
- **ReDoc**: `/api/redoc/`
- **OpenAPI Schema**: `/api/schema/`

## Rate Limiting

The API implements intelligent rate limiting:
- **Device-specific limits**: Protects individual network devices
- **User bypass capability**: Configurable for privileged users
- **Smart counting**: Only successful commands count toward limits
