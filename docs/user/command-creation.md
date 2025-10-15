# Command Creation

This guide explains how to create and manage network commands in the NetBox Toolkit Plugin.

## Overview

Commands are the core building blocks of the NetBox Toolkit Plugin. Each command defines:

- The network command to execute (e.g., `show version`, `show interfaces status`)
- The network platform it works with (Cisco IOS, Juniper JunOS, etc.)
- Command type (Show commands for read-only operations, Config commands for changes)
- Variables for dynamic command execution

## Creating Your First Command

### Step 1: Access Command Management
1. Log in to your NetBox instance
2. Click on **Command Toolkit > Commands** in the navigation bar
3. Click **"Add"** to create a new command

### Step 2: Basic Command Information
Fill in the essential command details:

- **Name**: A descriptive name that clearly indicates what the command does
    - Good: `"Show Interface Status"`, `"Check Device Version"`
    - Avoid: `"Command 1"`, `"Test"`

- **Command**: The actual network command to execute
    - Simple commands: `show version`, `show running-config`
    - Commands with variables: `show interface <interface_name> status`

- **Platform**: The network device platform this command works with
    - Common options: `cisco_ios`, `cisco_nxos`, `juniper_junos`, `arista_eos`

- **Command Type**: Choose the appropriate type:
    - **Show Command**: Read-only operations (monitoring, troubleshooting)
    - **Configuration Command**: Write operations (configuration changes)

### Step 3: Add Command Variables (Optional)
 It is possible to add varaibles to a command. Variable can be free text or can be linked to NetBox objects. Currently only interfaces, IP addresses and VLANs are supported as NetBox object types.

In the **Command** box, use snake_case - `<variable_name>` - syntax to define each variable.

For example:
```show interface <interface_name> status```

Or multiple variables in one command:
```ping <destination_ip> source <source_interface>```

1. Click **"Add Variable"** to create a new variable
2. Configure each variable:
    - **Name**: Variable identifier in snake_case (e.g., `interface_name`)
    - **Display Name**: User-friendly name (e.g., `Interface Name`)
    - **Variable Type**: Field type (Free Text or NetBox Object - Interface, IP Address, VLAN)
    - **Required**: Whether the variable must be filled
    - **Help Text**: Help text for users
    - **Default Value**: Optional default value

### Step 4: Save the Command
Click **"Create"** to save your new command.

## Command Examples by Platform

### Cisco IOS/IOS-XE
```
show version
show running-config
show interfaces status
show ip interface brief
show inventory
show environment all
show processes cpu sorted
show ip route
```

### Cisco NX-OS
```
show version
show running-config
show interface status
show ip interface brief
show inventory
show environment
show processes cpu sort
show ip route
```

### Juniper Junos
```
show version
show configuration
show interfaces terse
show chassis hardware
show chassis environment
show system processes extensive
show route
```

### Arista EOS
```
show version
show running-config
show interfaces status
show ip interface brief
show inventory
show environment all
show processes top
show ip route
```

### Command Organization
- **Naming Conventions**: Use consistent naming patterns (e.g., "Show - Interface Status", "Config - VLAN Setup")
- **Tags**: Apply tags to group related commands for easier filtering
- **Descriptions**: Provide clear descriptions of command purpose and expected output

### Platform-Specific Commands
- Always specify the correct platform when creating commands
- Consider platform-specific syntax differences
