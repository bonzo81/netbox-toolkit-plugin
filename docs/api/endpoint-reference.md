# API Endpoint Reference

Complete reference for all NetBox Toolkit Plugin API endpoints.

**Base URL:** `/api/plugins/toolkit/`

**Authentication:** All endpoints require NetBox API token authentication via `Authorization: Token YOUR_TOKEN` header.

---

## Commands

### List Commands
`GET /api/plugins/toolkit/commands/`

**Description:** Retrieve a list of all commands.

**Query Parameters:**

- `name` (string) - Filter by command name
- `command_type` (string) - Filter by type: `show` or `config`
- `platform_id` (integer) - Filter by platform ID
- `limit` (integer) - Number of results per page
- `offset` (integer) - Pagination offset

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `id` | integer | Unique command identifier |
| `url` | string | API URL for this command |
| `display` | string | Display representation |
| `name` | string | Command name |
| `command` | string | Actual command text |
| `description` | string | Command description |
| `platforms` | array | Array of platform objects |
| `command_type` | string | `show` or `config` |
| `variables` | array | Array of variable objects |
| `tags` | array | Array of tag objects |
| `custom_fields` | object | Custom field values |
| `created` | datetime | Creation timestamp |
| `last_updated` | datetime | Last update timestamp |

**Example Request:**
```bash
curl -H "Authorization: Token YOUR_TOKEN" \
  "https://netbox.example.com/api/plugins/toolkit/commands/?command_type=show"
```

**Example Response:**
```json
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "url": "https://netbox.example.com/api/plugins/toolkit/commands/1/",
      "display": "Show Interfaces",
      "name": "Show Interfaces",
      "command": "show interfaces <interface_name>",
      "description": "Display interface status and configuration",
      "platforms": [
        {
          "id": 5,
          "name": "Cisco IOS",
          "slug": "cisco_ios"
        }
      ],
      "command_type": "show",
      "variables": [
        {
          "id": 1,
          "name": "interface_name",
          "display_name": "Interface Name",
          "variable_type": "netbox_interface",
          "required": true,
          "help_text": "Select the interface to query",
          "default_value": ""
        }
      ],
      "tags": [],
      "custom_fields": {},
      "created": "2025-01-15T10:30:00Z",
      "last_updated": "2025-01-15T10:30:00Z"
    }
  ]
}
```

---

### Get Command
`GET /api/plugins/toolkit/commands/{id}/`

**Description:** Retrieve a specific command by ID.

**Path Parameters:**

- `id` (integer, required) - Command ID

**Response:** Same fields as List Commands (single object).

**Example Request:**
```bash
curl -H "Authorization: Token YOUR_TOKEN" \
  "https://netbox.example.com/api/plugins/toolkit/commands/1/"
```

---

### Create Command
`POST /api/plugins/toolkit/commands/`

**Description:** Create a new command.

**Request Body Fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | ✅ | Command name (max 100 characters) |
| `command` | string | ✅ | Command text (supports variables with `<variable_name>` syntax) |
| `description` | string | ❌ | Command description |
| `platforms` | array | ✅ | Array of platform IDs |
| `command_type` | string | ✅ | `show` or `config` |
| `tags` | array | ❌ | Array of tag objects |

**Example Request:**
```bash
curl -X POST -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Show Version",
    "command": "show version",
    "description": "Display system version information",
    "platforms": [5],
    "command_type": "show"
  }' \
  "https://netbox.example.com/api/plugins/toolkit/commands/"
```

---

### Update Command
`PUT /api/plugins/toolkit/commands/{id}/` (full update)
`PATCH /api/plugins/toolkit/commands/{id}/` (partial update)

**Description:** Update an existing command.

**Example Request:**
```bash
curl -X PATCH -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Updated description"
  }' \
  "https://netbox.example.com/api/plugins/toolkit/commands/1/"
```

---

### Delete Command
`DELETE /api/plugins/toolkit/commands/{id}/`

**Description:** Delete a command.

**Example Request:**
```bash
curl -X DELETE -H "Authorization: Token YOUR_TOKEN" \
  "https://netbox.example.com/api/plugins/toolkit/commands/1/"
```

---

### Execute Command
`POST /api/plugins/toolkit/commands/{id}/execute/`

**Description:** Execute a command on a device.

**Path Parameters:**

- `id` (integer, required) - Command ID

**Request Body Fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `device_id` | integer | ✅ | ID of target device |
| `credential_token` | string | ✅ | Credential token from DeviceCredentialSet |
| `variables` | object | ❌ | Key-value pairs for command variables |
| `timeout` | integer | ❌ | Timeout in seconds (5-300, default: 30) |

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `success` | boolean | Overall execution success |
| `output` | string | Command output |
| `error_message` | string | Error message if failed |
| `execution_time` | float | Execution duration in seconds |
| `command` | object | Command details (id, name, command_type) |
| `device` | object | Device details (id, name) |
| `syntax_error` | object | Syntax error detection details |
| `parsed_output` | object | Parsed output data if available |

**Example Request:**
```bash
curl -X POST -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": 123,
    "credential_token": "abc123def456",
    "variables": {
      "interface_name": "GigabitEthernet0/1"
    },
    "timeout": 30
  }' \
  "https://netbox.example.com/api/plugins/toolkit/commands/1/execute/"
```

**Example Response:**
```json
{
  "success": true,
  "output": "GigabitEthernet0/1 is up, line protocol is up...",
  "error_message": "",
  "execution_time": 2.34,
  "command": {
    "id": 1,
    "name": "Show Interface",
    "command_type": "show"
  },
  "device": {
    "id": 123,
    "name": "core-switch-01"
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

---

### Bulk Execute Commands
`POST /api/plugins/toolkit/commands/bulk-execute/`

**Description:** Execute commands on multiple devices simultaneously.

**Request Body Fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `executions` | array | ✅ | Array of execution objects |

**Execution Object Fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `command_id` | integer | ✅ | Command ID to execute |
| `device_id` | integer | ✅ | Target device ID |
| `credential_token` | string | ✅ | Credential token |
| `variables` | object | ❌ | Command variables |
| `timeout` | integer | ❌ | Timeout in seconds (5-300, default: 30) |

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `results` | array | Array of execution results |
| `summary` | object | Summary with total, successful, failed counts |

**Example Request:**
```bash
curl -X POST -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "executions": [
      {
        "command_id": 1,
        "device_id": 101,
        "credential_token": "abc123",
        "variables": {"vlan_id": "100"}
      },
      {
        "command_id": 1,
        "device_id": 102,
        "credential_token": "abc123",
        "variables": {"vlan_id": "100"}
      }
    ]
  }' \
  "https://netbox.example.com/api/plugins/toolkit/commands/bulk-execute/"
```

**Example Response:**
```json
{
  "results": [
    {
      "execution_id": 1,
      "success": true,
      "command_log_id": 501,
      "execution_time": 2.1
    },
    {
      "execution_id": 2,
      "success": true,
      "command_log_id": 502,
      "execution_time": 2.3
    }
  ],
  "summary": {
    "total": 2,
    "successful": 2,
    "failed": 0
  }
}
```

---

### Get Variable Choices
`GET /api/plugins/toolkit/commands/{id}/variable-choices/`

**Description:** Get available variable choices for a device.

**Path Parameters:**

- `id` (integer, required) - Command ID

**Query Parameters:**

- `device_id` (integer, required) - Device ID

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `device_id` | integer | Device ID |
| `device_name` | string | Device name |
| `command_id` | integer | Command ID |
| `command_name` | string | Command name |
| `variables` | object | Variable choices keyed by variable name |

**Example Request:**
```bash
curl -H "Authorization: Token YOUR_TOKEN" \
  "https://netbox.example.com/api/plugins/toolkit/commands/1/variable-choices/?device_id=123"
```

**Example Response:**
```json
{
  "device_id": 123,
  "device_name": "core-switch-01",
  "command_id": 1,
  "command_name": "Show Interface",
  "variables": {
    "interface_name": {
      "type": "netbox_interface",
      "choices": [
        {
          "value": "GigabitEthernet0/1",
          "display": "GigabitEthernet0/1 (1000base-t)",
          "id": 45,
          "enabled": true
        },
        {
          "value": "GigabitEthernet0/2",
          "display": "GigabitEthernet0/2 (1000base-t)",
          "id": 46,
          "enabled": true
        }
      ],
      "help_text": "Select the interface to query",
      "default_value": ""
    }
  }
}
```

---

## Command Logs

### List Command Logs
`GET /api/plugins/toolkit/command-logs/`

**Description:** Retrieve command execution history.

**Query Parameters:**

- `device_id` (integer) - Filter by device
- `command_id` (integer) - Filter by command
- `user_id` (integer) - Filter by user
- `success` (boolean) - Filter by success status
- `created__gte` (datetime) - Created after date
- `created__lte` (datetime) - Created before date
- `limit` (integer) - Results per page
- `offset` (integer) - Pagination offset

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `id` | integer | Log entry ID |
| `url` | string | API URL for this log |
| `display` | string | Display representation |
| `command` | object | Nested command object |
| `device` | object | Nested device object |
| `output` | string | Command output |
| `username` | string | User who executed command |
| `execution_time` | datetime | Execution timestamp |
| `success` | boolean | Execution success status |
| `error_message` | string | Error message if failed |
| `execution_duration` | float | Duration in seconds |
| `created` | datetime | Creation timestamp |
| `last_updated` | datetime | Last update timestamp |

**Example Request:**
```bash
curl -H "Authorization: Token YOUR_TOKEN" \
  "https://netbox.example.com/api/plugins/toolkit/command-logs/?device_id=123&success=true"
```

**Example Response:**
```json
{
  "count": 50,
  "next": "https://netbox.example.com/api/plugins/toolkit/command-logs/?limit=50&offset=50",
  "previous": null,
  "results": [
    {
      "id": 501,
      "url": "https://netbox.example.com/api/plugins/toolkit/command-logs/501/",
      "display": "Show Interface on core-switch-01",
      "command": {
        "id": 1,
        "name": "Show Interface",
        "display": "Show Interface"
      },
      "device": {
        "id": 123,
        "name": "core-switch-01",
        "display": "core-switch-01"
      },
      "output": "GigabitEthernet0/1 is up, line protocol is up...",
      "username": "admin",
      "execution_time": "2025-10-14T14:30:00Z",
      "success": true,
      "error_message": "",
      "execution_duration": 2.34,
      "created": "2025-10-14T14:30:00Z",
      "last_updated": "2025-10-14T14:30:00Z"
    }
  ]
}
```

---

### Get Command Log
`GET /api/plugins/toolkit/command-logs/{id}/`

**Description:** Retrieve a specific command log entry.

**Path Parameters:**

- `id` (integer, required) - Log entry ID

**Response:** Same fields as List Command Logs (single object).

**Example Request:**
```bash
curl -H "Authorization: Token YOUR_TOKEN" \
  "https://netbox.example.com/api/plugins/toolkit/command-logs/501/"
```

---

### Get Statistics
`GET /api/plugins/toolkit/command-logs/statistics/`

**Description:** Get comprehensive execution statistics.

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `total_logs` | integer | Total number of log entries |
| `success_rate` | float | Overall success rate percentage |
| `last_24h` | object | Statistics for last 24 hours |
| `top_commands` | array | Top 10 most-used commands |
| `common_errors` | array | Top 10 common error messages |

**Example Request:**
```bash
curl -H "Authorization: Token YOUR_TOKEN" \
  "https://netbox.example.com/api/plugins/toolkit/command-logs/statistics/"
```

**Example Response:**
```json
{
  "total_logs": 1523,
  "success_rate": 94.35,
  "last_24h": {
    "total": 145,
    "successful": 138,
    "failed": 7
  },
  "top_commands": [
    {
      "command_name": "Show Interfaces",
      "count": 423
    },
    {
      "command_name": "Show Version",
      "count": 312
    }
  ],
  "common_errors": [
    {
      "error": "Connection timeout",
      "count": 15
    },
    {
      "error": "Invalid credentials",
      "count": 8
    }
  ]
}
```

---

### Export Command Logs
`GET /api/plugins/toolkit/command-logs/export/`

**Description:** Export command logs to CSV or JSON.

**Query Parameters:**

- `format` (string) - Export format: `csv` or `json` (default: `json`)
- `start_date` (date) - Filter logs from date (YYYY-MM-DD)
- `end_date` (date) - Filter logs until date (YYYY-MM-DD)
- All standard filtering parameters from List Command Logs

**Response:** CSV file download or JSON array.

**Example Request (CSV):**
```bash
curl -H "Authorization: Token YOUR_TOKEN" \
  "https://netbox.example.com/api/plugins/toolkit/command-logs/export/?format=csv&start_date=2025-01-01&end_date=2025-12-31" \
  -o command_logs.csv
```

**Example Request (JSON):**
```bash
curl -H "Authorization: Token YOUR_TOKEN" \
  "https://netbox.example.com/api/plugins/toolkit/command-logs/export/?format=json&start_date=2025-10-01"
```

**Example Response (JSON):**
```json
{
  "count": 150,
  "results": [
    {
      "id": 501,
      "command": {
        "id": 1,
        "name": "Show Interface"
      },
      "device": {
        "id": 123,
        "name": "core-switch-01"
      },
      "username": "admin",
      "success": true,
      "created": "2025-10-14T14:30:00Z"
    }
  ]
}
```

---

## Error Responses

All endpoints may return the following error responses:

### 400 Bad Request
**Description:** Invalid request parameters or validation errors.

```json
{
  "device_id": [
    "Device not found"
  ]
}
```

### 401 Unauthorized
**Description:** Missing or invalid authentication token.

```json
{
  "detail": "Authentication credentials were not provided."
}
```

### 403 Forbidden
**Description:** User lacks required permissions.

```json
{
  "error": "You do not have permission to execute configuration commands"
}
```

### 404 Not Found
**Description:** Resource not found.

```json
{
  "detail": "Not found."
}
```

### 429 Too Many Requests
**Description:** Rate limit exceeded.

```json
{
  "error": "Rate limit exceeded",
  "details": {
    "reason": "Device rate limit exceeded",
    "current_count": 5,
    "limit": 5,
    "time_window_minutes": 60
  }
}
```

### 500 Internal Server Error
**Description:** Server-side error during processing.

```json
{
  "error": "An unexpected error occurred"
}
```

---

## Related Documentation

- [Authentication Guide](auth.md)
- [Command API Details](commands.md)
- [Command Logs API](command-logs.md)
- [Automation Examples](automation-examples.md)
- [API Workflows](workflows.md)
- [Error Handling](errors.md)
