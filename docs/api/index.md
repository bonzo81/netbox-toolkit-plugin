# API Reference

The NetBox Toolkit Plugin provides a comprehensive REST API for network device command execution and management.

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
- **Key Features**: CRUD operations, command execution, bulk operations

### [Command Logs API](command-logs.md)
- **Purpose**: Track command execution history and results
- **Endpoints**: `/command-logs/`
- **Key Features**: Execution history, statistics, export capabilities

### [Authentication & Permissions](auth.md)
- **Purpose**: Security and access control
- **Key Features**: Token authentication, object permissions, action permissions

### [Error Handling](errors.md)
- **Purpose**: Error codes and troubleshooting
- **Key Features**: Error structure, common errors, resolution strategies

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
