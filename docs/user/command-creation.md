# Command Creation Guide

Learn how to create and organize commands for different network platforms.

## Overview

Before executing commands on devices, you need to define reusable commands via the plugin menu. This guide walks you through the command creation process.

Make sure to understand the different command types and their usage before proceeding.

## Command Types

### Show Commands
Read-only operations that retrieve information:

- Status and monitoring commands
- Configuration display commands

**Examples**: `show version`, `show interfaces`, `show ip route`

### Configuration Commands
Commands that modify device configuration:

- Interface configuration
- Routing protocol configuration
- System configuration changes

**Examples**: `interface GigabitEthernet1/1`, `router ospf 1`, `hostname new-name`

> ⚠️ **Warning**: Configuration commands can impact network operations. Use appropriate permissions and testing procedures.

### Benefits of using command types:

- **Permissions Control** - Users can be restricted to executing only show commands
- **Output Parsing** - Show commands are parsed for structured output, config commands are not

## Creating Commands

### 1. Plugin Command Toolkit Menu

1. Navigate to **Plugins > Command Toolkit > Commands**
2. Click **"Add"** to create a new command

### 2. Fill Command Details

Complete the following fields:

- **Name**: A descriptive name (e.g., "Show Interface Status")
- **Command**: The actual command to execute with optional variables
  - Basic command: `show version`
  - With variables: `show interface <interface_name> status`
  - Multiple variables: `show access-list <acl_name> line <line_number>`
  > Use full command syntax for optimal TextFSM template parsing
- **Description**: Optional explanation of what the command does
- **Platform**: The device platform this command is designed for (e.g., `cisco_ios`, `cisco_nxos`, `arista_eos`)
- **Command Type**: Choose from:
    - `Show Command` - Read-only operations
    - `Configuration Command` - Write operations
- **Tags**: Optional tags for better organization

### 3. Define Command Variables (Optional)

If your command includes variables (text within angle brackets `<>`), you'll need to define them:

#### Variable Syntax Requirements

Variables must follow these formatting rules:

- **Correct Format**: `<variable_name>` - enclosed in angle brackets
- **Valid Names**: Must start with a letter or underscore, followed by letters, numbers, or underscores
- **Examples of Valid Variables**:
  - `<interface_name>` ✅
  - `<vlan_id>` ✅
  - `<access_list_name>` ✅
  - `<_private_var>` ✅

- **Examples of Invalid Variables**:
  - `<123invalid>` ❌ (starts with number)
  - `<var-name>` ❌ (contains hyphen)
  - `<var name>` ❌ (contains space)
  - `<var.name>` ❌ (contains period)

#### Variable Types

For each variable in your command, specify:

- **Name**: The exact variable name from your command (without angle brackets)
- **Display Name**: User-friendly name shown in forms
- **Type**: Choose the appropriate variable type:
  - **Free Text** - Any text input (e.g., hostnames, descriptions)
  - **Device Interface** - Dropdown of available interfaces from NetBox
  - **VLAN** - VLAN selection from NetBox data
  - **IP Address** - IP addresses assigned to the device
- **Required**: Whether the variable must be provided
- **Help Text**: Optional guidance for users
- **Default Value**: Optional pre-filled value

#### Example Variable Configuration

For command: `show interface <interface_name> status`

| Field | Value |
|-------|-------|
| Name | `interface_name` |
| Display Name | `Interface Name` |
| Type | `Device Interface` |
| Required | ✅ Yes |
| Help Text | `Select the interface to check` |

### 4. Save the Command

Click **"Create"** to save the command. The system will automatically:
- Validate variable syntax in your command
- Ensure all variables have corresponding definitions
- Remove any orphaned variable definitions



## Variable Validation & Troubleshooting

### Common Variable Errors

The system validates variable syntax when saving commands. Here are common issues and solutions:

#### Invalid Variable Names
**Error**: "Invalid variable name '<var-name>'. Variable names must start with a letter or underscore..."

**Solutions**:
- Replace hyphens with underscores: `<var-name>` → `<var_name>`
- Replace spaces with underscores: `<var name>` → `<var_name>`
- Don't start with numbers: `<123var>` → `<var_123>`

#### Missing Variable Definitions
**Error**: "Command references undefined variables: variable_name"

**Solution**: Add a variable definition in the Variables section for each `<variable_name>` in your command.

#### Orphaned Variables
**Behavior**: Variables are automatically removed if they're no longer referenced in the command text.

### Variable Execution Flow

1. **Command Creation**: Define command with `<variable_name>` syntax
2. **Variable Configuration**: Set up variable types and validation rules
3. **Command Execution**: Users provide values through dynamic forms
4. **Variable Substitution**: System replaces `<variable_name>` with actual values
5. **Command Execution**: Processed command runs on target device

### Complete Variable Examples

#### Example 1: Interface Status Check
```
Command: show interface <interface_name> status
Variables:
- Name: interface_name
- Type: Device Interface
- Display: Interface Name
```

#### Example 2: Multi-Variable VLAN Configuration
```
Command: interface <interface_name>
         switchport access vlan <vlan_id>
         description <description>
Variables:
- interface_name (Device Interface)
- vlan_id (VLAN)
- description (Free Text)
```

#### Example 3: Access Control Lists
```
Command: show access-list <acl_name> line <line_number>
Variables:
- acl_name (Free Text)
- line_number (Free Text)
```

## Best Practices

### Command Naming
- Use descriptive, consistent names (e.g., "Show Interface Status", "Configure VLAN", "Show Routing Table")
- Include platform in name if creating platform-specific variants
- Group related commands with consistent prefixes

### Variable Design
- **Use descriptive variable names**: `<interface_name>` instead of `<int>`
- **Choose appropriate types**: Use NetBox data types for validation when possible
- **Provide helpful text**: Guide users with clear help text and examples
- **Set sensible defaults**: Pre-fill common values where appropriate

### Command Organization
- **Group by function**: Interface commands, routing commands, system commands
- **Use tags effectively**: Tag commands by category (monitoring, troubleshooting, configuration)
- **Platform-specific commands**: Create separate commands for each platform rather than generic ones

### TextFSM Integration
- Use complete command syntax (e.g., `show ip interface brief` instead of `sh ip int br`)
- Full commands provide better TextFSM template matching
- Structured output parsing works best with standard command formats

### Security Considerations
- **Show commands**: Generally safe for all users
- **Configuration commands**: Restrict to senior engineers and administrators
- **Variable validation**: NetBox data types provide built-in validation (interfaces must exist on device)
- **Sensitive commands**: Be cautious with commands that might reveal credentials or security information


## Next Steps

After creating commands:

1. **Set up permissions** - Configure who can execute which commands [📖 Permissions Setup Guide](./permissions-setup-guide.md)

2. **Monitor usage** - Review command logs for performance and security
3. **Enable logging** for troubleshooting (optional) [� Logging Guide](./logging.md)
