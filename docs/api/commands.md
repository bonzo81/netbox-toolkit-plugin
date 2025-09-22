# Commands API

The Commands API allows you to manage network commands with variables and execute them on devices. The API provides comprehensive support for command variables that can reference NetBox data like interfaces, VLANs, and IP addresses.

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
| POST | `/commands/{id}/validate-variables/` | Validate command variables |
| GET | `/commands/{id}/variable-choices/` | Get variable choices for a device |
| POST | `/commands/bulk-execute/` | Execute multiple commands |

## Command Variables

Commands can include variables that are dynamically replaced with values during execution. Variables are defined using angle bracket syntax: `<variable_name>`.

### Variable Types

| Type | Description | Example Value | Validation |
|------|-------------|---------------|------------|
| `text` | Free text input | `"any text"` | None |
| `netbox_interface` | Device interface | `"GigabitEthernet0/1"` | Must exist on device |
| `netbox_vlan` | VLAN ID | `"100"` | Must exist on device/site |
| `netbox_ip` | IP address | `"192.168.1.1"` | Must be assigned to device |

### Example Command with Variables

```json
{
    "name": "Show Interface Status",
    "command": "show interface <interface_name> status",
    "platforms": [1],
    "command_type": "show",
    "description": "Display status of a specific interface",
    "variables": [
        {
            "name": "interface_name",
            "display_name": "Interface Name",
            "variable_type": "netbox_interface",
            "required": true,
            "help_text": "Select the interface to check"
        }
    ]
}
```

## Working with Variables

### 1. Discovery: Get Available Variable Choices

Before executing a command with variables, discover what values are available for the target device:

```bash
GET /api/plugins/toolkit/commands/{id}/variable-choices/?device_id={device_id}
```

**Example Request:**
```bash
GET /api/plugins/toolkit/commands/1/variable-choices/?device_id=123
```

**Response:**
```json
{
    "device_id": 123,
    "device_name": "switch01.example.com",
    "command_id": 1,
    "command_name": "Show Interface Status",
    "variables": {
        "interface_name": {
            "type": "netbox_interface",
            "choices": [
                {
                    "value": "GigabitEthernet0/1",
                    "display": "GigabitEthernet0/1 (1000base-t)",
                    "id": 456,
                    "enabled": true
                },
                {
                    "value": "GigabitEthernet0/2",
                    "display": "GigabitEthernet0/2 (1000base-t)",
                    "id": 457,
                    "enabled": false
                }
            ],
            "help_text": "Select the interface to check",
            "default_value": ""
        }
    }
}
```

### 2. Validation: Check Variables Before Execution

Validate variable values without executing the command:

```bash
POST /api/plugins/toolkit/commands/{id}/validate-variables/
```

**Request:**
```json
{
    "variables": {
        "interface_name": "GigabitEthernet0/1"
    }
}
```

**Success Response:**
```json
{
    "detail": "Variables are valid"
}
```

**Error Response:**
```json
{
    "variables": {
        "interface_name": "Interface 'GigabitEthernet0/99' not found on device 'switch01'. Available interfaces: GigabitEthernet0/1, GigabitEthernet0/2, ..."
    }
}
```

### 3. Execution: Run Command with Variables

Execute a command with validated variables:

```bash
POST /api/plugins/toolkit/commands/{id}/execute/
```

**Request:**
```json
{
    "device_id": 123,
    "username": "admin",
    "password": "password123",
    "variables": {
        "interface_name": "GigabitEthernet0/1"
    },
    "timeout": 30
}
```

**Response:**
```json
{
    "success": true,
    "output": "GigabitEthernet0/1 is up, line protocol is up...",
    "error_message": null,
    "execution_time": "2025-06-13T10:30:45.123Z",
    "command": {
        "id": 1,
        "name": "Show Interface Status",
        "command_type": "show",
        "original_text": "show interface <interface_name> status",
        "executed_text": "show interface GigabitEthernet0/1 status"
    },
    "device": {
        "id": 123,
        "name": "switch01"
    },
    "variables": {
        "interface_name": "GigabitEthernet0/1"
    },
    "syntax_error": {
        "detected": false
    },
    "parsed_output": {
        "success": true,
        "method": "textfsm",
        "data": [
            {
                "interface": "GigabitEthernet0/1",
                "status": "up",
                "protocol": "up"
            }
        ]
    }
}
```

## Variable Workflow Example

Here's a complete workflow for working with variable commands via API:

```python
import requests

# 1. Get command information including variables
command = requests.get("/api/plugins/toolkit/commands/1/").json()
print(f"Command: {command['name']}")
print(f"Variables: {[v['name'] for v in command['variables']]}")

# 2. Get available choices for the target device
choices = requests.get(
    "/api/plugins/toolkit/commands/1/variable-choices/?device_id=123"
).json()

# 3. Present choices to user and collect input
interface_choices = choices['variables']['interface_name']['choices']
print("Available interfaces:")
for choice in interface_choices:
    print(f"  {choice['value']} - {choice['display']}")

selected_interface = "GigabitEthernet0/1"  # User selection

# 4. Validate before execution (optional but recommended)
validation = requests.post(
    "/api/plugins/toolkit/commands/1/validate-variables/",
    json={"variables": {"interface_name": selected_interface}}
)
print(f"Validation: {validation.json()}")

# 5. Execute with validated variables
result = requests.post(
    "/api/plugins/toolkit/commands/1/execute/",
    json={
        "device_id": 123,
        "username": "admin",
        "password": "password",
        "variables": {"interface_name": selected_interface}
    }
)
print(f"Execution result: {result.json()}")
```

## Creating Commands

### Basic Command Creation

```bash
POST /api/plugins/toolkit/commands/
```

```json
{
    "name": "Show Interfaces",
    "command": "show ip interface brief",
    "platforms": [1],
    "command_type": "show",
    "description": "Display interface status summary"
}
```

### Command with Variables

When creating commands with variables, the variables are managed separately through the admin interface or forms. The API response will include variable definitions:

```json
{
    "id": 1,
    "name": "Show Interface Config",
    "command": "show running-config interface <interface_name>",
    "platforms": [1],
    "command_type": "show",
    "description": "Show configuration for a specific interface",
    "variables": [
        {
            "id": 1,
            "name": "interface_name",
            "display_name": "Interface Name",
            "variable_type": "netbox_interface",
            "required": true,
            "help_text": "Select the interface to configure",
            "default_value": ""
        }
    ]
}
```

### Command Types

- **`show`**: Read-only commands that display information
- **`config`**: Configuration commands that modify device state

## Bulk Command Execution

Execute multiple commands across multiple devices with variable support:

```bash
POST /api/plugins/toolkit/commands/bulk-execute/
```

**Request Format:**
```json
{
    "executions": [
        {
            "command_id": 1,
            "device_id": 123,
            "username": "admin",
            "password": "password123",
            "variables": {
                "interface_name": "GigabitEthernet0/1"
            }
        },
        {
            "command_id": 2,
            "device_id": 124,
            "username": "admin",
            "password": "password123",
            "variables": {
                "vlan_id": "100"
            }
        }
    ]
}
```

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
            "error": "Variable validation failed",
            "details": {
                "variables": {
                    "vlan_id": "VLAN 100 not found for device 'router01' or its site"
                }
            }
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
| `platforms` | Platform ID | `?platforms=1` |
| `platforms__slug` | Platform slug | `?platforms__slug=cisco_ios` |
| `command_type` | Command type | `?command_type=show` |
| `description__icontains` | Description contains | `?description__icontains=interface` |

## Error Handling

### Variable Validation Errors

When variable validation fails, the API returns detailed error information:

```json
{
    "variables": {
        "interface_name": "Interface 'FastEthernet0/99' not found on device 'switch01'. Available interfaces: GigabitEthernet0/1, GigabitEthernet0/2, ..."
    }
}
```

### Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `Device with ID X not found` | Invalid device_id | Verify device exists |
| `Interface 'X' not found on device` | Interface doesn't exist | Use variable-choices endpoint to get valid options |
| `VLAN X not found for device` | VLAN not available | Check device site VLANs |
| `IP address 'X' is not associated with device` | IP not assigned to device | Verify IP assignment |
| `Missing required variable: X` | Required variable not provided | Include all required variables |

### Best Practices

1. **Always check variable choices** before execution for NetBox data variables
2. **Validate variables** before execution to catch errors early
3. **Handle validation errors** gracefully in your applications
4. **Use meaningful variable names** that match the command context
5. **Set appropriate help text** for variables to guide users
