# NetBox Toolkit Plugin - Permissions Setup Guide

This guide shows how to set up permissions for the NetBox Toolkit Plugin using NetBox's Object-Based Permission system through the web interface.

## Overview

The NetBox Toolkit Plugin uses NetBox's built-in [Object-Based Permission](https://docs.netbox.dev/en/stable/administration/permissions/) system to provide granular access control for:

- **Command Management** (create, edit, delete commands)
- **Command Execution** (run show commands vs config commands)
- **Command Log Access** (view execution history)

Make sure to understand how to [create commands](./command-creation.md) before proceeding with permissions.

## Permission Options Overview

The plugin uses NetBox's ObjectPermission system with these 3 key permission options:

### 1. Standard Permissions
- **View** - View command lists and details
- **Add** - Create new commands
- **Change** - Edit existing commands  
- **Delete** - Remove commands

### 2. Custom Actions
- **`execute_show`** - Execute show/monitoring commands (read-only operations)
- **`execute_config`** - Execute configuration commands (write operations)

### 3. Contraints
- **Constraints** - Filter available commands further by json command attributes (optional)


For Step by step examples, see the [Permission Examples](./permission-examples.md) page.

## Constraints Support
NetBox permissions allow you to limit permissions further by using JSON constraints:
```json
# Filter by platform
{"platform__slug": "cisco_ios"}  // Only Cisco IOS commands
```

#### Advanced Constraint Examples

**AND Logic** (all conditions must be true):
```json
# Filter by command type AND platform
{
  "command_type": "show",
  "platform__slug": "cisco_ios"
}
```

**OR Logic** (any condition can be true) - uses array format:
```json
# Filter by platform (cisco_ios OR cisco_nxos)
[
  {"platform__slug": "cisco_ios"},
  {"platform__slug": "cisco_nxos"}
]
```

**Field Value Lists** (match any value in list similar to OR logic):
```json
# Filter by platform (cisco_ios OR cisco_nxos OR juniper_junos)
{"platform__slug__in": ["cisco_ios", "cisco_nxos", "juniper_junos"]}
```

**Text Pattern Matching**:
```json
# 3 Examples of Filtering by name pattern

{"name__icontains": "version"}      // Name contains "version" (case-insensitive)

{"name__startswith": "show"}        // Name starts with "show"

{"description__contains": "safe"}   // Description contains "safe" (case-sensitive)
```

### Basic Contraints Example: 
Users Can Only View and Execute "show version" Commands
Permission 1: View Subset of Commands
```
Name: "Toolkit - View Show Version Commands Only"
Object Types: Command Toolkit | command
Actions: ✓ view
Additional Actions: (leave empty)
Constraints: {"name__icontains": "show version"}
Groups: Junior Network Engineers
```
Permission 2: Execute Subset of Commands
```
Name: "Toolkit - Execute Show Version Commands Only"
Object Types: Command Toolkit | command
Actions: (leave unchecked)
Additional Actions: execute_show
Constraints: {"name__icontains": "show version"}
Groups: Junior Network Engineers
```

## Constraint Further Info

Constraints use Django ORM [field lookups](https://docs.djangoproject.com/en/5.2/ref/models/querysets/#field-lookups) based on the Command model fields and related models.

Here are some common lookups you can use:

**Common Field Lookups:**

- `field` - Exact match
- `field__in` - Match any value in list  
- `field__icontains` - Case-insensitive contains
- `field__startswith` - Starts with value
- `field__gte` - Greater than or equal
- `field__lt` - Less than
- `field__contains` - Case-sensitive contains

**Related Field Lookups:**

- `platform__slug` - Access platform's slug field
- `platform__name` - Access platform's name field  
- `tags__name` - Access tag name (many-to-many relationship)

