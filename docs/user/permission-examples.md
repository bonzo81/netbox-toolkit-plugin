# NetBox Toolkit Plugin - Permission Examples

This page provides complete step-by-step examples for setting up permissions for the NetBox Toolkit Plugin using NetBox's Object-Based Permission system.


## Permission Example

Below are the groups that we will be use for the permissions example. Each of these groups will be assigned specific permissions.

1. **Junior Network Engineers**
2. **Senior Network Engineers**
3. **Network Administrators**

### Desired User Matrix

The desired user capabilities for our example are as follows:

| User Role | View Commands | Execute Show | Execute Config | Manage Commands | View Logs | Manage Logs |
|-----------|---------------|--------------|----------------|-----------------|-----------|-------------|
| **Junior Network Engineers** | ✅ | ✅ (show only) | ❌ | ❌ | ✅ | ❌ |
| **Senior Network Engineers** | ✅ | ✅ | ✅ | ❌ | ✅ | ❌ |
| **Network Administrators** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |


## Permission Design

### Granular Permission Design

To achieve the above we need to create **reusable permissions** that can then be assigned to multiple groups or users.

Here are the permissions we will setup:

| Permission | Purpose | Applied to Groups |
|------------|---------|------------------|
| **Command Toolkit - View Commands** | View command list and details | All groups |
| **Command Toolkit - Execute Show Commands** | Execute show/monitoring commands only | All groups |
| **Command Toolkit - Execute Config Commands** | Execute configuration commands | Senior Engineers, Admins |
| **Command Toolkit - Manage Commands** | Create, edit, delete commands | Admins only |
| **Command Toolkit - View Command Logs** | View execution history | All groups |
| **Command Toolkit - Manage Command Logs** | Manage log entries | Admins only |


## Create Groups

WE will now create the groups and permission above and assign to users.

### Step 1: Create User Groups

1. Navigate to **Admin → Users → Groups**
2. Click **+ Add Group** to create each of the following groups:

#### Group 1: Junior Network Engineers
- **Name**: `Junior Network Engineers`
- **Permissions**: Leave empty (we'll use NetBox Permissions)
- **Save**

#### Group 2: Senior Network Engineers
- **Name**: `Senior Network Engineers`
- **Permissions**: Leave empty (we'll use NetBox Permissions)
- **Save**

#### Group 3: Network Administrators
- **Name**: `Network Administrators`
- **Permissions**: Leave empty (we'll use NetBox Permissions)
- **Save**

## Create Permissions & Assign to Groups

Navigate to **Admin → Users → Permissions** and create the following **reusable permissions**:

#### Permission 1: Toolkit - View Commands
- **Name**: `Toolkit - View Commands`
- **Object Types**: Select `Command Toolkit | command`
- **Actions**: Check `view`
- **Additional Actions**: Leave empty
- **Groups**: Select `Junior Network Engineers`, `Senior Network Engineers`, `Network Administrators`
- **Enabled**: ✓
- **Save**

#### Permission 2: Toolkit - Execute Show Commands
- **Name**: `Toolkit - Execute Show Commands`
- **Object Types**: Select `Command Toolkit | command`
- **Actions**: Leave the checkboxes empty
- **Additional Actions**: Type `execute_show`
- **Groups**: Select `Junior Network Engineers`, `Senior Network Engineers`, `Network Administrators`
- **Enabled**: ✓
- **Save**

#### Permission 3: Toolkit - Execute Config Commands
- **Name**: `Toolkit - Execute Config Commands`
- **Object Types**: Select `Command Toolkit | command`
- **Actions**: Leave the checkboxes empty
- **Additional Actions**: Type `execute_config`
- **Groups**: Select `Senior Network Engineers`, `Network Administrators` (NOT Junior Engineers)
- **Enabled**: ✓
- **Save**

#### Permission 4: Toolkit - Manage Commands
- **Name**: `Toolkit - Manage Commands`
- **Object Types**: Select `Command Toolkit | command`
- **Actions**: Check `add`, `change`, `delete`
- **Additional Actions**: Leave empty
- **Groups**: Select `Network Administrators` (ONLY Admins)
- **Enabled**: ✓
- **Save**

#### Permission 5: Toolkit - View Command Logs
- **Name**: `Toolkit - View Command Logs`
- **Object Types**: Select `Command Toolkit | command log`
- **Actions**: Check `view`
- **Additional Actions**: Leave empty
- **Groups**: Select `Junior Network Engineers`, `Senior Network Engineers`, `Network Administrators`
- **Enabled**: ✓
- **Save**

#### Permission 6: Toolkit - Manage Command Logs
- **Name**: `Toolkit - Manage Command Logs`
- **Object Types**: Select `Command Toolkit | command log`
- **Actions**: Check `add`, `change`, `delete`
- **Additional Actions**: Leave empty
- **Groups**: Select `Network Administrators` (ONLY Admins)
- **Enabled**: ✓
- **Save**

## Assign Users to Groups

1. Navigate to **Admin → Users → Users**
2. Click on a user to edit them
3. In the **Groups** section, select the appropriate group(s)
4. **Save**

## Advanced Examples with Constraints

### Example 1: Restricted View and Execute Permissions

**Scenario**: Users can only view and execute the "show version" command specifically.

#### Permission 1: View Show Version Commands Only
```json
Name: "Toolkit - View Show Version Commands Only"
Object Types: Command Toolkit | command
Actions: ✓ view
Additional Actions: (leave empty)
Constraints: {
  "command_type": "show",
  "name": "Show Version"
}
Groups: Junior Network Engineers
```

#### Permission 2: Execute Show Version Commands Only
```json
Name: "Toolkit - Execute Show Version Commands Only"
Object Types: Command Toolkit | command
Actions: (leave unchecked)
Additional Actions: execute_show
Constraints: {
  "command_type": "show",
  "name": "Show Version"
}
Groups: Junior Network Engineers
```

**Result**: Users can only see and execute commands that:
- Are of type "show" (read-only operations)
- Command name is exactly "Show Version"

### Example 2: Platform-Specific Permissions

**Scenario**: Network team can only view and execute Cisco platform commands.

#### Permission 1: View Cisco Commands
```json
Name: "Toolkit - View Cisco Commands"
Object Types: Command Toolkit | command
Actions: ✓ view
Constraints: {
  "platform__slug__in": ["cisco_ios", "cisco_nxos", "cisco_iosxr"]
}
Groups: Network Team
```

#### Permission 2: Execute Cisco Show Commands
```json
Name: "Toolkit - Execute Cisco Show Commands"
Object Types: Command Toolkit | command
Additional Actions: execute_show
Constraints: {
  "command_type": "show",
  "platform__slug__in": ["cisco_ios", "cisco_nxos", "cisco_iosxr"]
}
Groups: Network Team
```

### Example 3: Tag-Based Command Access

**Scenario**: Users can only access commands tagged as "safe" or "monitoring".

#### Permission: Safe Monitoring Commands
```json
Name: "Toolkit - Safe Monitoring Commands"
Object Types: Command Toolkit | command
Actions: ✓ view
Additional Actions: execute_show
Constraints: {
  "command_type": "show",
  "tags__name__in": ["safe", "monitoring"]
}
Groups: Monitoring Team
```
