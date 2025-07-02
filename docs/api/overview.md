# API Overview

This page provides a high-level overview of the NetBox Toolkit API. For specific endpoints and detailed functionality, please refer to the dedicated API documentation pages.

## Features

The NetBox Toolkit Plugin provides a comprehensive REST API for network device command execution with the following features:

- **Command Management**: CRUD operations for network commands
- **Command Execution**: Execute commands on devices with proper validation
- **Bulk Operations**: Execute multiple commands across multiple devices
- **Rate Limiting**: Built-in protection against excessive API usage
- **Permissions Integration**: Leverages NetBox's ObjectPermission system
- **Comprehensive Filtering**: Advanced filtering and search capabilities

## API Structure

The API is organized into distinct resources:

| Resource | Description | Documentation |
|----------|-------------|---------------|
| Commands | Manage and execute network commands | [Commands API](commands.md) |
| Command Logs | Track command execution history | [Command Logs API](command-logs.md) |

## Authentication and Security

All API endpoints require authentication using NetBox's token system. For details, see the [Authentication & Permissions](auth.md) documentation.

## Error Handling

The API provides consistent error formats and appropriate HTTP status codes. For details, see the [Error Handling](errors.md) documentation.

