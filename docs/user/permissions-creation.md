# Permissions Creation

This guide shows how to set up permissions for the NetBox Toolkit Plugin.

The Toolkit Plugin uses NetBox's built-in Object-Based Permission system. This allows for very granular access control, but can seem confusing at first. The plugin permissions can control access to the following features:

- **Command Management** (create, edit, delete commands)
- **Command Execution** (run show commands vs config commands)
- **Command Log Access** (view command execution history)
- **Credential Set Management** (create, view, use credentials)

## NetBox Permission System Overview

The plugin uses NetBox's ObjectPermission system with these key components:

### 1. Standard Permissions
- **View**: View command lists and details, credential sets, command logs
- **Add**: Create new commands and credential sets
- **Change**: Edit existing commands and credential sets
- **Delete**: Remove commands and credential sets

### 2. Custom Actions
- **`execute_show`**: Execute show/monitoring commands (read-only operations)
- **`execute_config`**: Execute configuration commands (write operations)

### 3. Toolkit Plugin Object Types
- **Command**: Network command definitions
- **Command Log**: Command execution history
- **Device Credential Set**: Secure credential storage

## Creating Permissions

### Step 1: Goto Permission Management Page
1. Log in to NetBox as a **superuser** or **administrator**
2. Navigate to **Admin > Permissions**
3. Click **"Add"** to create a new permission

### Step 2: Configure Basic Permission Details
1. **Name**: Descriptive name (e.g., "Toolkit - Execute Show Commands Only")
2. **Actions**: Choose from View, Add, Change, Delete
3. **Additional Actions**: Type `execute_show` and/or `execute_config` as needed
4. **Object Types**: Select the appropriate object types:
    - `Toolkit Plugin | Command` for command permissions
    - `Toolkit Plugin | Command Log` for log access
    - `Toolkit Plugin | Device Credential Set` for credential access
5. **Constraints** (optional): Use JSON to filter permissions further (see below)
> Important: Any user that will execute commands will need View, Add, Change, Delete permission for 'Command Toolkit | devicecredentialset'


### Step 3: Assign to Users/Groups

The permission needs to be assinged to user or groups. This can be done on the permiosson screen or in the Users or Groups admin pages.


## Permission Examples

### Example 1: Junior Network Engineers
**Show Command Execution Only**
```
Name: "Toolkit - Junior Engineers - Show Commands Only"
Object Types: Command Toolkit | command
Actions: ✓ view
Additional Actions: execute_show
Constraints: {"command_type": "show"}
Groups: Junior Network Engineers
```

**Command Log Access**
```
Name: "Toolkit - Junior Engineers - Command Logs"
Object Types: Command Toolkit | commandlog
Actions: ✓ view
Groups: Junior Network Engineers
```

**Credential Permission**
```
Name: "Toolkit - Credential Sets"
Object Types: Command Toolkit | devicecredentialset
Actions: ✓ view, ✓ add, ✓ change, ✓ delete
Groups: Junior Network Engineers
```

### Example 2: Senior Network Engineers
**Full Command Management**
```
Name: "Toolkit - Senior Engineers - Full Access"
Object Types: Command Toolkit | command
Actions: ✓ view, ✓ add, ✓ change, ✓ delete
Additional Actions: execute_show, execute_config
Groups: Senior Network Engineers
```

**Credential Permission**
```
Name: "Toolkit - Credential Sets"
Object Types: Command Toolkit | devicecredentialset
Actions: ✓ view, ✓ add, ✓ change, ✓ delete
Groups: Senior Network Engineers
```

## Using Constraints

Constraints use Django ORM field lookups to filter permissions based on object attributes.

### Basic Constraint Examples

#### Filter by Command Type
```json
{"command_type": "show"}
```
Only allows access to show commands.

#### Filter by Platform
```json
{"platform__slug": "cisco_ios"}
```
Only allows access to Cisco IOS commands.

#### Filter by Command Name
```json
{"name__icontains": "version"}
```
Only allows access to commands containing "version".

### Advanced Constraint Examples

#### AND Logic (all conditions must be true)
```json
{
  "command_type": "show",
  "platform__slug": "cisco_ios"
}
```
Only show commands on Cisco IOS platforms.

#### OR Logic (any condition can be true)
```json
[
  {"platform__slug": "cisco_ios"},
  {"platform__slug": "cisco_nxos"}
]
```
Commands on either Cisco IOS or NX-OS platforms.

#### Field Value Lists
```json
{"platform__slug__in": ["cisco_ios", "cisco_nxos", "juniper_junos"]}
```
Commands on any of the specified platforms.

#### Text Pattern Matching
```json
{"name__icontains": "interface"}
```
Commands with "interface" in the name (case-insensitive).


## Troubleshooting

### Common Permission Issues

#### Users Can't See Commands
- **Check**: Verify user has "View" permission on Command Toolkit | command
- **Solution**: Add view permission or check constraints

#### Users Can't Execute Commands
- **Check**: Verify user has execute_show or execute_config permissions
- **Solution**: Add appropriate execution permissions

