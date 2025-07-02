# Authentication & Permissions

The NetBox Toolkit API integrates with NetBox's built-in authentication and permission system.

## Authentication

### API Token Authentication

All API requests require authentication using NetBox's token system:

```bash
curl -H "Authorization: Token YOUR_TOKEN_HERE" \
     -H "Content-Type: application/json" \
     https://netbox.example.com/api/plugins/toolkit/commands/
```

### Getting Your API Token

1. **Via NetBox Web UI:**
   - Log into NetBox
   - Go to User → Profile → API Tokens
   - Create a new token or copy an existing one

2. **Via Django Admin:**
   - Access Django admin interface
   - Navigate to Auth Token → Tokens
   - Create or view existing tokens

## Permissions

The plugin uses NetBox's ObjectPermission system with custom actions for command execution.

### Permission Actions

| Action | Description | Applies To |
|--------|-------------|------------|
| `view` | View commands and logs | Commands, Command Logs |
| `add` | Create new commands | Commands |
| `change` | Modify existing commands | Commands |
| `delete` | Delete commands | Commands |
| `execute_show` | Execute show commands | Commands |
| `execute_config` | Execute configuration commands | Commands |

### Setting Up Permissions

#### 1. Create User Groups

```python
# Example: Create groups for different access levels
from django.contrib.auth.models import Group

# Read-only users
readonly_group = Group.objects.create(name='Toolkit Read Only')

# Show command executors
show_executors = Group.objects.create(name='Toolkit Show Commands')

# Full access (show + config commands)
full_access = Group.objects.create(name='Toolkit Full Access')
```

#### 2. Create Object Permissions

```python
from users.models import ObjectPermission
from django.contrib.contenttypes.models import ContentType
from netbox_toolkit.models import Command

# Get content type for Command model
command_ct = ContentType.objects.get_for_model(Command)

# Permission to execute show commands
show_permission = ObjectPermission.objects.create(
    name='Execute Show Commands',
    enabled=True,
    object_types=[command_ct],
    actions=['execute_show'],
    constraints={'command_type': 'show'}  # Only show commands
)
show_permission.groups.add(show_executors)

# Permission to execute config commands
config_permission = ObjectPermission.objects.create(
    name='Execute Config Commands',
    enabled=True,
    object_types=[command_ct],
    actions=['execute_config'],
    constraints={'command_type': 'config'}  # Only config commands
)
config_permission.groups.add(full_access)
```

#### 3. Assign Users to Groups

```python
from django.contrib.auth.models import User

# Assign user to show executors group
user = User.objects.get(username='john_doe')
user.groups.add(show_executors)
```

### Permission Constraints

You can restrict permissions using constraints:

#### Platform-Specific Permissions

```python
# Only allow execution on Cisco IOS devices
ios_permission = ObjectPermission.objects.create(
    name='Execute on Cisco IOS Only',
    enabled=True,
    object_types=[command_ct],
    actions=['execute_show'],
    constraints={'platform__slug': 'cisco_ios'}
)
```

#### Command-Specific Permissions

```python
# Only allow specific commands
version_permission = ObjectPermission.objects.create(
    name='Execute Version Commands Only',
    enabled=True,
    object_types=[command_ct],
    actions=['execute_show'],
    constraints={'name__icontains': 'version'}
)
```

## Rate Limiting & Bypass

### Rate Limiting Permissions

Users and groups can bypass rate limiting through plugin configuration:

```python
# In NetBox configuration.py
PLUGINS_CONFIG = {
    'netbox_toolkit': {
        'rate_limiting_enabled': True,
        'device_command_limit': 10,
        'time_window_minutes': 5,
        'bypass_users': ['admin', 'automation_user'],
        'bypass_groups': ['Toolkit Admins', 'Automation Systems'],
    }
}
```

### Checking Rate Limit Status

Rate limiting information is included in permission checks and API responses.

## Common Permission Scenarios

### Scenario 1: Network Operators (Show Commands Only)

```python
# Create group
operators = Group.objects.create(name='Network Operators')

# Create permission for show commands
show_perm = ObjectPermission.objects.create(
    name='Network Operators - Show Commands',
    enabled=True,
    object_types=[command_ct],
    actions=['view', 'execute_show'],
    constraints={'command_type': 'show'}
)
show_perm.groups.add(operators)
```

### Scenario 2: Network Engineers (Full Access)

```python
# Create group
engineers = Group.objects.create(name='Network Engineers')

# Create permission for all commands
full_perm = ObjectPermission.objects.create(
    name='Network Engineers - Full Access',
    enabled=True,
    object_types=[command_ct],
    actions=['view', 'add', 'change', 'delete', 'execute_show', 'execute_config']
)
full_perm.groups.add(engineers)
```

### Scenario 3: Automation Systems

```python
# Create group with rate limit bypass
automation = Group.objects.create(name='Automation Systems')

# Full permissions
automation_perm = ObjectPermission.objects.create(
    name='Automation - Full Access',
    enabled=True,
    object_types=[command_ct],
    actions=['view', 'execute_show', 'execute_config']
)
automation_perm.groups.add(automation)

# Add to bypass groups in configuration
PLUGINS_CONFIG = {
    'netbox_toolkit': {
        'bypass_groups': ['Automation Systems'],
    }
}
```

## API Permission Errors

### Common Error Responses

#### 401 Unauthorized
```json
{
    "detail": "Authentication credentials were not provided."
}
```

#### 403 Forbidden
```json
{
    "error": "You do not have permission to execute configuration commands"
}
```

#### 429 Too Many Requests (Rate Limiting)
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

## Best Practices

1. **Use Groups**: Assign permissions to groups rather than individual users
2. **Principle of Least Privilege**: Only grant necessary permissions
3. **Use Constraints**: Restrict permissions to specific platforms or command types
4. **Rate Limit Bypass**: Only grant to trusted automation systems
5. **Regular Audits**: Review and audit permissions regularly
6. **Test Permissions**: Verify permissions work as expected before deploying
