# Commands API

The Commands API allows you to manage network commands and execute them on devices.

## Endpoints Overview

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/commands/` | List all commands |
| POST | `/commands/` | Create a new command |
| GET | `/commands/{id}/` | Retrieve a specific command |
| PUT | `/commands/{id}/` | Update a command |
| PATCH | `/commands/{id}/` | Partially update a command |
| DELETE | `/commands/{id}/` | Delete a command |
| POST | `/commands/{id}/execute/` | Execute a command |
| POST | `/commands/bulk-execute/` | Execute multiple commands |

## Creating Commands

### Basic Command Creation

```bash
POST /api/plugins/toolkit/commands/
```

```json
{
    "name": "Show Interfaces",
    "command": "show ip interface brief",
    "platform": 1,
    "command_type": "show",
    "description": "Display interface status summary"
}
```

### Command Types

- **`show`**: Read-only commands that display information
- **`config`**: Configuration commands that modify device state

## Command Execution

### Single Command Execution

Execute a command on a specific device:

```bash
POST /api/plugins/toolkit/commands/{id}/execute/
```

**Request:**
```json
{
    "device_id": 123,
    "username": "admin",
    "password": "password123",
    "timeout": 30
}
```

**Response:**
```json
{
    "success": true,
    "output": "Cisco IOS Software, Version 15.1(4)M12a...",
    "error_message": null,
    "execution_time": "2025-06-13T10:30:45.123Z",
    "command": {
        "id": 1,
        "name": "Show Version",
        "command_type": "show"
    },
    "device": {
        "id": 123,
        "name": "switch01"
    },
    "syntax_error": {
        "detected": false
    },
    "parsed_output": {
        "success": true,
        "method": "textfsm",
        "data": [
            {
                "version": "15.1(4)M12a",
                "hostname": "switch01",
                "uptime": "1 year, 23 weeks, 4 days"
            }
        ]
    }
}
```

### Bulk Command Execution

Execute multiple commands across multiple devices:

```bash
POST /api/plugins/toolkit/commands/bulk-execute/
```

**Request Format:**
The request must be an object with an `executions` array. Each execution object requires:
- `command_id`: ID of the command to execute
- `device_id`: ID of the target device  
- `username`: Authentication username
- `password`: Authentication password

```json
{
    "executions": [
        {
            "command_id": 1,
            "device_id": 123,
            "username": "admin",
            "password": "password123"
        },
        {
            "command_id": 2,
            "device_id": 124,
            "username": "admin",
            "password": "password123"
        }
    ]
}
```

> **⚠️ Important:** The request must be wrapped in an `executions` object. Sending a plain array will result in a 400 error.

**Response:**
```json
{
    "results": [
        {
            "execution_id": 1,
            "success": true,
            "command_log_id": 456,
            "execution_time": 1.23
        },
        {
            "execution_id": 2,
            "success": false,
            "error": "Connection timeout"
        }
    ],
    "summary": {
        "total": 2,
        "successful": 1,
        "failed": 1
    }
}
```

## Filtering Commands

| Filter | Description | Example |
|--------|-------------|---------|
| `name` | Exact name match | `?name=Show%20Version` |
| `name__icontains` | Name contains (case-insensitive) | `?name__icontains=version` |
| `platform` | Platform ID | `?platform=1` |
| `platform__slug` | Platform slug | `?platform__slug=cisco_ios` |
| `command_type` | Command type | `?command_type=show` |
| `description__icontains` | Description contains | `?description__icontains=interface` |

## Examples

### Get all show commands for Cisco IOS
```bash
GET /api/plugins/toolkit/commands/?platform__slug=cisco_ios&command_type=show
```

### Execute a command with custom timeout
```bash
POST /api/plugins/toolkit/commands/1/execute/
{
    "device_id": 123,
    "username": "admin", 
    "password": "secret",
    "timeout": 60
}
```

### Search for interface-related commands
```bash
GET /api/plugins/toolkit/commands/?name__icontains=interface
```

## Troubleshooting

### Common Bulk Execution Errors

**❌ Incorrect Format (400 Error)**
```json
// DON'T send a plain array
[
    {
        "command_id": 9,
        "device_id": 24,
        "username": "user",
        "password": "password"
    }
]
```

**✅ Correct Format**
```json
// DO wrap in "executions" object
{
    "executions": [
        {
            "command_id": 9,
            "device_id": 24,
            "username": "user",
            "password": "password"
        }
    ]
}
```

### Error Messages

| Error | Cause | Solution |
|-------|-------|----------|
| `'list' object has no attribute 'get'` | Sending plain array instead of object | Wrap executions in `executions` key |
| `Missing required fields` | Missing command_id, device_id, username, or password | Include all required fields |
| `Object not found` | Invalid command_id or device_id | Verify IDs exist in the system |
| `Insufficient permissions` | User lacks execute permissions | Check NetBox object permissions |
