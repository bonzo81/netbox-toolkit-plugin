"""
OpenAPI schema definitions for NetBox Toolkit API
"""
from drf_spectacular.utils import extend_schema, OpenApiResponse


# Command ViewSet Schemas
COMMAND_LIST_SCHEMA = extend_schema(
    summary="List commands",
    description="Retrieve a list of all commands available in the system.",
    tags=["Commands"]
)

COMMAND_RETRIEVE_SCHEMA = extend_schema(
    summary="Retrieve command",
    description="Retrieve details of a specific command.",
    tags=["Commands"]
)

COMMAND_CREATE_SCHEMA = extend_schema(
    summary="Create command",
    description="Create a new command.",
    tags=["Commands"]
)

COMMAND_UPDATE_SCHEMA = extend_schema(
    summary="Update command",
    description="Update an existing command.",
    tags=["Commands"]
)

COMMAND_PARTIAL_UPDATE_SCHEMA = extend_schema(
    summary="Partial update command",
    description="Partially update an existing command.",
    tags=["Commands"]
)

COMMAND_DESTROY_SCHEMA = extend_schema(
    summary="Delete command",
    description="Delete a command.",
    tags=["Commands"]
)

COMMAND_EXECUTE_SCHEMA = extend_schema(
    summary="Execute command on device",
    description="Execute a specific command on a target device with authentication credentials.",
    tags=["Commands"],
    responses={
        200: OpenApiResponse(
            description="Command executed successfully",
            examples=[
                {
                    "success": True,
                    "output": "interface status output...",
                    "error_message": None,
                    "execution_time": 1.23,
                    "command": {
                        "id": 1,
                        "name": "show interfaces",
                        "command_type": "show"
                    },
                    "device": {
                        "id": 1,
                        "name": "switch01.example.com"
                    },
                    "syntax_error": {
                        "detected": False
                    },
                    "parsed_output": {
                        "success": True,
                        "method": "textfsm",
                        "data": [{"interface": "GigabitEthernet1/0/1", "status": "up"}]
                    }
                }
            ]
        ),
        400: OpenApiResponse(
            description="Bad request - validation errors or command execution failed"
        ),
        403: OpenApiResponse(
            description="Forbidden - insufficient permissions"
        ),
        404: OpenApiResponse(
            description="Not found - command or device not found"
        ),
        429: OpenApiResponse(
            description="Too many requests - rate limit exceeded"
        )
    }
)

COMMAND_BULK_EXECUTE_SCHEMA = extend_schema(
    summary="Bulk execute commands",
    description="Execute multiple commands on multiple devices in a single API call.",
    tags=["Commands"],
    request={
        "type": "object",
        "properties": {
            "executions": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "command_id": {"type": "integer"},
                        "device_id": {"type": "integer"},
                        "username": {"type": "string"},
                        "password": {"type": "string", "format": "password"}
                    },
                    "required": ["command_id", "device_id", "username", "password"]
                }
            }
        },
        "required": ["executions"]
    },
    responses={
        200: OpenApiResponse(
            description="Bulk execution completed",
            examples=[
                {
                    "results": [
                        {"execution_id": 1, "success": True, "command_log_id": 123},
                        {"execution_id": 2, "success": False, "error": "Permission denied"}
                    ],
                    "summary": {
                        "total": 2,
                        "successful": 1,
                        "failed": 1
                    }
                }
            ]
        )
    }
)

# Command Log ViewSet Schemas
COMMAND_LOG_LIST_SCHEMA = extend_schema(
    summary="List command logs",
    description="Retrieve a list of command execution logs with filtering and search capabilities.",
    tags=["Command Logs"]
)

COMMAND_LOG_RETRIEVE_SCHEMA = extend_schema(
    summary="Retrieve command log",
    description="Retrieve details of a specific command execution log.",
    tags=["Command Logs"]
)

COMMAND_LOG_CREATE_SCHEMA = extend_schema(
    summary="Create command log",
    description="Create a new command execution log entry.",
    tags=["Command Logs"]
)

COMMAND_LOG_UPDATE_SCHEMA = extend_schema(
    summary="Update command log",
    description="Update an existing command log entry.",
    tags=["Command Logs"]
)

COMMAND_LOG_PARTIAL_UPDATE_SCHEMA = extend_schema(
    summary="Partial update command log",
    description="Partially update an existing command log entry.",
    tags=["Command Logs"]
)

COMMAND_LOG_DESTROY_SCHEMA = extend_schema(
    summary="Delete command log",
    description="Delete a command log entry.",
    tags=["Command Logs"]
)

COMMAND_LOG_STATISTICS_SCHEMA = extend_schema(
    summary="Get command log statistics",
    description="Retrieve statistics about command execution logs including success rates and common errors.",
    tags=["Command Logs"],
    responses={
        200: OpenApiResponse(
            description="Statistics retrieved successfully",
            examples=[
                {
                    "total_logs": 1000,
                    "success_rate": 85.5,
                    "last_24h": {
                        "total": 50,
                        "successful": 45,
                        "failed": 5
                    },
                    "top_commands": [
                        {"command_name": "show interfaces", "count": 150},
                        {"command_name": "show version", "count": 120}
                    ],
                    "common_errors": [
                        {"error": "Connection timeout", "count": 10},
                        {"error": "Invalid command", "count": 5}
                    ]
                }
            ]
        )
    }
)

from drf_spectacular.utils import OpenApiParameter

COMMAND_LOG_EXPORT_SCHEMA = extend_schema(
    summary="Export command logs",
    description="Export command logs in various formats (CSV, JSON).",
    tags=["Command Logs"],
    parameters=[
        OpenApiParameter(
            name='format',
            description='Export format',
            required=False,
            type=str,
            enum=['csv', 'json'],
            default='json'
        ),
        OpenApiParameter(
            name='start_date',
            description='Start date for export (YYYY-MM-DD)',
            required=False,
            type=str
        ),
        OpenApiParameter(
            name='end_date',
            description='End date for export (YYYY-MM-DD)',
            required=False,
            type=str
        ),
    ],
    responses={
        200: OpenApiResponse(description="Export data"),
        400: OpenApiResponse(description="Invalid parameters")
    }
)
