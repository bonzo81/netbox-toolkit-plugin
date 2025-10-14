# Error Handling

The NetBox Toolkit API provides comprehensive error handling with detailed error messages and appropriate HTTP status codes.

## HTTP Status Codes

### Success Codes
- **200 OK**: Request successful
- **201 Created**: Resource created successfully

### Client Error Codes
- **400 Bad Request**: Invalid input or execution failed
- **401 Unauthorized**: Authentication required
- **403 Forbidden**: Permission denied
- **404 Not Found**: Resource not found
- **429 Too Many Requests**: Rate limit exceeded

### Server Error Codes
- **500 Internal Server Error**: Unexpected server error

## Error Response Format

All API errors follow a consistent format:

```json
{
    "error": "Brief error description",
    "details": {
        "field_name": ["Detailed error message"],
        "another_field": ["Another error message"]
    }
}
```

## Common Error Scenarios

### 1. Authentication Errors

#### Missing Token
```http
HTTP/1.1 401 Unauthorized
```
```json
{
    "detail": "Authentication credentials were not provided."
}
```

#### Invalid Token
```http
HTTP/1.1 401 Unauthorized
```
```json
{
    "detail": "Invalid token."
}
```

### 2. Permission Errors

#### Insufficient Permissions
```http
HTTP/1.1 403 Forbidden
```
```json
{
    "error": "You do not have permission to execute configuration commands"
}
```

#### Object Not Found (Due to Permissions)
```http
HTTP/1.1 404 Not Found
```
```json
{
    "detail": "Not found."
}
```

### 3. Rate Limiting Errors

#### Rate Limit Exceeded
```http
HTTP/1.1 429 Too Many Requests
```
```json
{
    "error": "Rate limit exceeded",
    "details": {
        "reason": "Rate limit exceeded: 10/10 successful commands in last 5 minutes",
        "current_count": 10,
        "limit": 10,
        "time_window_minutes": 5
    }
}
```

### 4. Validation Errors

#### Missing Required Fields
```http
HTTP/1.1 400 Bad Request
```
```json
{
    "error": "Invalid input data",
    "details": {
        "device_id": ["This field is required."],
        "username": ["This field is required."]
    }
}
```

#### Invalid Field Values
```http
HTTP/1.1 400 Bad Request
```
```json
{
    "error": "Invalid input data",
    "details": {
        "device_id": ["Invalid pk \"999\" - object does not exist."],
        "command_type": ["\"invalid\" is not a valid choice."]
    }
}
```

### 5. Command Execution Errors

#### Device Not Found
```http
HTTP/1.1 404 Not Found
```
```json
{
    "error": "Device with ID 999 not found"
}
```

#### Connection Failed
```http
HTTP/1.1 400 Bad Request
```
```json
{
    "success": false,
    "output": "",
    "error_message": "Connection timeout: Unable to connect to device",
    "execution_time": null,
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
    }
}
```

#### Authentication Failed
```http
HTTP/1.1 400 Bad Request
```
```json
{
    "success": false,
    "output": "",
    "error_message": "Authentication failed: Invalid credentials",
    "execution_time": null,
    "command": {
        "id": 1,
        "name": "Show Version",
        "command_type": "show"
    },
    "device": {
        "id": 123,
        "name": "switch01"
    }
}
```

#### Syntax Error Detected
```http
HTTP/1.1 400 Bad Request
```
```json
{
    "success": false,
    "output": "% Invalid input detected at '^' marker.",
    "error_message": "Command execution failed",
    "execution_time": 0.5,
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
        "detected": true,
        "type": "invalid_input",
        "vendor": "cisco",
        "guidance_provided": true
    }
}
```

### 6. Bulk Operation Errors

#### Partial Failure
```http
HTTP/1.1 200 OK
```
```json
{
    "results": [
        {
            "execution_id": 1,
            "success": true,
            "command_log_id": 123,
            "execution_time": 1.5
        },
        {
            "execution_id": 2,
            "success": false,
            "error": "Device with ID 999 not found"
        },
        {
            "execution_id": 3,
            "success": false,
            "error": "Insufficient permissions"
        }
    ],
    "summary": {
        "total": 3,
        "successful": 1,
        "failed": 2
    }
}
```

#### No Executions Provided
```http
HTTP/1.1 400 Bad Request
```
```json
{
    "error": "No executions provided"
}
```

### 7. Export Errors

#### Export Too Large
```http
HTTP/1.1 400 Bad Request
```
```json
{
    "error": "Export too large. Please use date filters to reduce size."
}
```

#### Invalid Date Format
```http
HTTP/1.1 400 Bad Request
```
```json
{
    "error": "Invalid start_date format. Use YYYY-MM-DD."
}
```

## Error Handling Best Practices


### 1. Check Status Codes
Always check HTTP status codes to determine the type of error:

```python
import requests

response = requests.post(
    'https://netbox.example.com/api/plugins/toolkit/commands/1/execute/',
    headers={'Authorization': 'Token your-token'},
    json={'device_id': 123, 'username': 'admin', 'password': 'secret'}
)

if response.status_code == 200:
    result = response.json()
    if result['success']:
        print("Command executed successfully")
    else:
        print(f"Command failed: {result['error_message']}")
elif response.status_code == 400:
    print("Bad request:", response.json())
elif response.status_code == 403:
    print("Permission denied:", response.json())
elif response.status_code == 429:
    print("Rate limited:", response.json())
else:
    print(f"Unexpected error {response.status_code}:", response.json())
```

### 2. Handle Rate Limiting Gracefully

```python
import time

def execute_with_retry(command_id, device_id, username, password, max_retries=3):
    for attempt in range(max_retries):
        response = requests.post(
            f'https://netbox.example.com/api/plugins/toolkit/commands/{command_id}/execute/',
            headers={'Authorization': 'Token your-token'},
            json={
                'device_id': device_id,
                'username': username,
                'password': password
            }
        )

        if response.status_code == 429:
            # Rate limited, wait and retry
            retry_after = int(response.headers.get('Retry-After', 60))
            print(f"Rate limited, waiting {retry_after} seconds...")
            time.sleep(retry_after)
            continue

        return response

    raise Exception("Max retries exceeded")
```

### 3. Validate Input Before Sending

```python
def validate_execution_request(device_id, username, password):
    errors = []

    if not device_id:
        errors.append("device_id is required")
    if not username:
        errors.append("username is required")
    if not password:
        errors.append("password is required")

    if errors:
        raise ValueError(f"Validation errors: {', '.join(errors)}")
```

### 4. Log Errors for Debugging

```python
import logging

logger = logging.getLogger(__name__)

def execute_command(command_id, device_id, username, password):
    try:
        response = requests.post(...)

        if response.status_code != 200:
            logger.error(
                f"Command execution failed: {response.status_code} - {response.text}"
            )

        return response
    except requests.exceptions.RequestException as e:
        logger.error(f"Network error during command execution: {e}")
        raise
```

## Getting Help

If you encounter persistent errors:

1. Check the [NetBox logs](../user/logging.md) for detailed error information
2. Verify your [permissions setup](../user/permissions-creation.md)
3. Review the [configuration guide](../user/plugin-configuration.md)
3. Check for common issues in the [Permission Examples](../user/permission-examples.md) section
4. Check the [GitHub issues](https://github.com/yourusername/netbox-toolkit-plugin/issues) for known problems
