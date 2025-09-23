# Command Logs API

The Command Logs API provides access to command execution history, statistics, and export capabilities. This API offers **enhanced analytics capabilities** not available in the web interface, making it ideal for monitoring, reporting, and operational insights.

## API-Exclusive Features

📊 **Advanced Statistics**: Comprehensive execution analytics including success rates, trending, and performance metrics
📈 **Operational Insights**: Identify top commands, common errors, and usage patterns
📅 **Flexible Export**: Advanced export options with date filtering and multiple formats

All web interface functionality is also fully supported via API for complete feature parity.

## Endpoints Overview

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/command-logs/` | List all command logs |
| GET | `/command-logs/{id}/` | Retrieve a specific log |
| GET | `/command-logs/statistics/` | Get execution statistics |
| GET | `/command-logs/export/` | Export logs (CSV/JSON) |

!!! note
    Command logs are created automatically when commands are executed. Manual creation via POST is generally not needed.

## Command Log Object

```json
{
    "id": 456,
    "url": "/api/plugins/toolkit/command-logs/456/",
    "display": "Show Version on switch01 - 2025-06-13 10:30:45",
    "command": {
        "id": 1,
        "name": "Show Version",
        "command_type": "show",
        "url": "/api/plugins/toolkit/commands/1/"
    },
    "device": {
        "id": 123,
        "name": "switch01",
        "url": "/api/dcim/devices/123/"
    },
    "output": "Cisco IOS Software, Version 15.1(4)M12a...",
    "username": "admin",
    "execution_time": "2025-06-13T10:30:45.123Z",
    "success": true,
    "error_message": null,
    "execution_duration": 1.23,
    "parsed_data": {
        "version": "15.1(4)M12a",
        "hostname": "switch01",
        "uptime": "1 year, 23 weeks, 4 days"
    },
    "parsing_success": true,
    "parsing_template": "cisco_ios_show_version.textfsm",
    "created": "2025-06-13T10:30:45.123Z",
    "last_updated": "2025-06-13T10:30:45.123Z"
}
```

## Statistics

**API-Exclusive Feature**: Get comprehensive statistics about command executions for operational insights and monitoring.

### Use Cases
- **Performance Monitoring**: Track success rates and identify problematic commands
- **Usage Analytics**: Understand which commands are used most frequently
- **Error Analysis**: Identify common failure patterns and troubleshoot issues
- **Capacity Planning**: Monitor execution volumes and trends over time

Get comprehensive statistics about command executions:

```bash
GET /api/plugins/toolkit/command-logs/statistics/
```

**Response:**
```json
{
    "total_logs": 1000,
    "success_rate": 85.5,
    "last_24h": {
        "total": 50,
        "successful": 45,
        "failed": 5
    },
    "top_commands": [
        {
            "command_name": "show interfaces",
            "count": 150
        },
        {
            "command_name": "show version",
            "count": 120
        }
    ],
    "common_errors": [
        {
            "error": "Connection timeout",
            "count": 10
        },
        {
            "error": "Invalid command",
            "count": 5
        }
    ]
}
```

## Export

Export command logs in CSV or JSON format:

```bash
GET /api/plugins/toolkit/command-logs/export/?format=csv&start_date=2025-06-01&end_date=2025-06-30
```

### Export Parameters

| Parameter | Description | Example |
|-----------|-------------|---------|
| `format` | Export format (csv/json) | `format=csv` |
| `start_date` | Start date filter (YYYY-MM-DD) | `start_date=2025-06-01` |
| `end_date` | End date filter (YYYY-MM-DD) | `end_date=2025-06-30` |

!!! warning "Export Limits"
    Exports are limited to 10,000 records for performance. Use date filters to reduce result size.

## Filtering Command Logs

| Filter | Description | Example |
|--------|-------------|---------|
| `command` | Command ID | `?command=1` |
| `device` | Device ID | `?device=123` |
| `username` | Exact username | `?username=admin` |
| `username__icontains` | Username contains | `?username__icontains=adm` |
| `success` | Execution success | `?success=true` |
| `parsing_success` | Parsing success | `?parsing_success=true` |
| `has_parsed_data` | Has parsed data | `?has_parsed_data=true` |
| `execution_time__gte` | Executed after | `?execution_time__gte=2025-06-01` |
| `execution_time__lte` | Executed before | `?execution_time__lte=2025-06-30` |
| `device__name__icontains` | Device name contains | `?device__name__icontains=switch` |
| `command__name__icontains` | Command name contains | `?command__name__icontains=version` |

## Examples

### Get recent failed executions
```bash
GET /api/plugins/toolkit/command-logs/?success=false&execution_time__gte=2025-06-01
```

### Get logs for a specific device
```bash
GET /api/plugins/toolkit/command-logs/?device=123&ordering=-execution_time
```

### Export last month's logs as CSV
```bash
GET /api/plugins/toolkit/command-logs/export/?format=csv&start_date=2025-05-01&end_date=2025-05-31
```

### Get logs with parsing failures
```bash
GET /api/plugins/toolkit/command-logs/?parsing_success=false&success=true
```

### Search for specific error messages
```bash
GET /api/plugins/toolkit/command-logs/?success=false&search=timeout
```
