# Commands API

## Overview

The Commands API enables automated execution of network commands on devices with full support for variables, bulk operations, and integration workflows. This API provides capabilities beyond the web interface for automation and system integration.

## Key Capabilities

**API-Exclusive Features:**

- 🚀 **Bulk Execution**: Execute multiple commands across multiple devices in a single API call
- 🔍 **Variable Discovery**: Programmatically retrieve available NetBox data choices for any device
- ✅ **Enhanced Validation**: Comprehensive variable validation integrated with command execution
- 📊 **Advanced Integration**: Perfect for automation workflows, CI/CD pipelines, and third-party integrations

**Full Feature Parity**: All web interface functionality is supported via API for complete automation capability.

## Authentication & Credentials

The Commands API uses **NetBox authentication with credential tokens** for enhanced security:

1. **NetBox API Token**: Standard NetBox authentication (sent in `Authorization` header)
2. **Credential Token**: References stored device credentials (sent in request body)

### Why Two Tokens?

- **Security**: Device credentials are never transmitted in API calls
- **User Isolation**: Users can only use their own stored credential sets
- **Audit Trail**: All actions are properly logged to user accounts
- **Flexibility**: Multiple credential sets can be managed per user

### Setting Up Credentials


1. Create a **Device Credential Set** in the NetBox web interface
2. Store your device username/password (encrypted automatically)
3. Copy the generated **credential token** for API use
4. Use both your NetBox API token and credential token in API calls

### Example API Call

```bash
curl -X POST "https://netbox.example.com/api/plugins/toolkit/commands/17/execute/" \
  -H "Authorization: Token <your-netbox-api-token>" \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": 1,
    "credential_token": "<your-credential-token>"
  }'
```

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


## Understanding Variable Validation Types

The API provides **comprehensive variable validation** integrated with command execution:

### Enhanced Validation (`/execute/`)

**What it validates:**
- ✅ Variable definitions exist for command
- ✅ Required variables have values
- ✅ Variable substitution syntax is correct
- ✅ Interface/VLAN/IP existence on target device
- ✅ User permissions for device/command
- ✅ Credential validity

**Use case:** Complete validation and command execution in one step

### Discovery (`/variable-choices/`)

**What it provides:**
- ✅ Available interfaces for a device
- ✅ Available VLANs for a device/site
- ✅ Available IP addresses for a device
- ✅ Variable metadata and help text

**Use case:** Building dynamic forms or validating against real data

## Variable Workflow

Here's how the endpoints work together for variable commands:

```mermaid
graph TD
    A[Start with Command] --> B[/variable-choices/?device_id=X]
    B --> C[Get available interfaces/VLANs/IPs]
    C --> D[Present choices to user]
    D --> E[User selects values]
    E --> F[/execute/]
    F --> G{Validation and execution successful?}
    G -->|Yes| H[Command executed successfully]
    G -->|No| I[Show validation/execution errors]
    I --> B
```

### Recommended Workflow

1. **Discovery Phase**: Use `/variable-choices/` to get valid options for a device
2. **Selection Phase**: Present options to user and collect their selections
3. **Execution Phase**: Use `/execute/` for comprehensive validation and command execution
4. **Error Handling**: The `/execute/` endpoint provides detailed error messages for both validation and execution issues

### 4. Execution: Run Command with Variables

Execute a command with validated variables:

```bash
POST /api/plugins/toolkit/commands/{id}/execute/
```

**Request:**
```json
{
    "device_id": 123,
    "credential_token": "HsAo6NEoNcWYaE0hi_B9PqC6NcV-IZgwbLgDw_rR1I_1awHhUQMhhWrMMPIZjVvBrIi8fXDAmQfx8BXJoF1LNg",
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
    "execution_time": 0.9740488529205322,
    "command": {
        "id": 1,
        "name": "Show Interface Status",
        "command_type": "show"
    },
    "device": {
        "id": 123,
        "name": "switch01"
    },
    "credential_set": {
        "id": 8,
        "name": "Network Admin Credentials"
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
}
```

## Variable Workflow Example

Here's a complete workflow for working with variable commands via API:

```python
import requests

# Configuration
BASE_URL = "https://netbox.example.com"
API_TOKEN = "your-netbox-api-token"
CREDENTIAL_TOKEN = "your-credential-token"  # From Device Credential Set

headers = {
    "Authorization": f"Token {API_TOKEN}",
    "Content-Type": "application/json"
}

# 1. Get command information including variables
command = requests.get(f"{BASE_URL}/api/plugins/toolkit/commands/1/", headers=headers).json()
print(f"Command: {command['name']}")
print(f"Variables: {[v['name'] for v in command['variables']]}")

# 2. Get available choices for the target device
choices = requests.get(
    f"{BASE_URL}/api/plugins/toolkit/commands/1/variable-choices/?device_id=123",
    headers=headers
).json()

# 3. Present choices to user and collect input
interface_choices = choices['variables']['interface_name']['choices']
print("Available interfaces:")
for choice in interface_choices:
    print(f"  {choice['value']} - {choice['display']}")

selected_interface = "GigabitEthernet0/1"  # User selection

# 4. Execute with enhanced validation (includes all validation checks)
result = requests.post(
    f"{BASE_URL}/api/plugins/toolkit/commands/1/execute/",
    headers=headers,
    json={
        "device_id": 123,
        "credential_token": CREDENTIAL_TOKEN,
        "variables": {"interface_name": selected_interface}
    }
)

if result.json()["success"]:
    print(f"Execution successful: {result.json()['output']}")
else:
    print(f"Execution failed: {result.json()['error_message']}")
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

**API-Exclusive Feature**: Execute multiple commands across multiple devices with variable support. This powerful capability enables automation scenarios not possible through the web interface.

### Use Cases
- **Network-wide Configuration**: Deploy configuration changes across multiple devices
- **Mass Data Collection**: Gather information from entire device groups
- **Automated Auditing**: Run compliance checks across your infrastructure
- **Orchestrated Workflows**: Execute complex multi-device operations

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
            "credential_token": "HsAo6NEoNcWYaE0hi_B9PqC6NcV-IZgwbLgDw_rR1I_1awHhUQMhhWrMMPIZjVvBrIi8fXDAmQfx8BXJoF1LNg",
            "variables": {
                "interface_name": "GigabitEthernet0/1"
            }
        },
        {
            "command_id": 2,
            "device_id": 124,
            "credential_token": "HsAo6NEoNcWYaE0hi_B9PqC6NcV-IZgwbLgDw_rR1I_1awHhUQMhhWrMMPIZjVvBrIi8fXDAmQfx8BXJoF1LNg",
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

#### `/execute/` and `/variable-choices/` Errors (Device-Specific)

```json
{
    "variables": {
        "interface_name": "Interface 'FastEthernet0/99' not found on device 'switch01'. Available interfaces: GigabitEthernet0/1, GigabitEthernet0/2, ..."
    }
}
```

```json
{
    "variables": {
        "vlan_id": "VLAN 999 not found for device 'switch01' or its site"
    }
}
```

### Common Errors by Type

#### Device Context Errors (`/execute/`, `/variable-choices/`)
| Error | Cause | Solution |
|-------|-------|----------|
| `Device with ID X not found` | Invalid device_id | Verify device exists in NetBox |
| `Interface 'X' not found on device` | Interface doesn't exist | Use `/variable-choices/` endpoint to get valid options |
| `VLAN X not found for device` | VLAN not available | Check device site VLANs or use `/variable-choices/` |
| `IP address 'X' is not associated with device` | IP not assigned to device | Verify IP assignment in NetBox |

## Best Practices

### Variable Management
1. **Use `/variable-choices/` endpoint** to get valid options for NetBox data variables before execution
2. **Perform comprehensive validation** using `/execute/` endpoint which includes all validation checks
3. **Handle validation errors gracefully** - the `/execute/` endpoint provides detailed error messages
4. **Use meaningful variable names** that match the command context

### Error Handling
1. **Check HTTP status codes** for different error types
2. **Implement retry logic** for rate limiting (429 responses)
3. **Log detailed error information** for debugging
4. **Validate input** before sending API requests

### Performance
1. **Use bulk execution** for multiple devices when possible
2. **Batch requests** to avoid API limits
3. **Cache variable choices** when executing similar commands
4. **Monitor rate limits** and implement backoff strategies

## Related Documentation
- **Setup**: [Authentication Guide](auth.md)
- **Examples**: [API Automation Examples](automation-examples.md)
- **Authentication**: [Authentication & Permissions](auth.md)
- **Troubleshooting**: [Error Handling](errors.md)
