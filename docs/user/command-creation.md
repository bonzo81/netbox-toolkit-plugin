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

- **Name**: A descriptive name (e.g., "Show Version")
- **Command**: The actual command to execute (e.g., `show version`) 
  > Use full command syntax for optimal TextFSM template parsing
- **Description**: Optional explanation of what the command does
- **Platform**: The device platform this command is designed for (e.g., `cisco_ios`, `cisco_nxos`, `arista_eos`)
- **Command Type**: Choose from:
    - `Show Command` - Read-only operations
    - `Configuration Command` - Write operations
- **Tags**: Optional tags for better organization

### 3. Save the Command

Click **"Create"** to save the command for use across your devices.



## Best Practices

### Command Naming
- Use descriptive, consistent names (e.g., "Show Version", "Show Interfaces", "Show Routing Table")
- Include platform in name if creating platform-specific variants
- Group related commands with consistent prefixes

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
- **Sensitive commands**: Be cautious with commands that might reveal credentials or security information


## Next Steps

After creating commands:

1. **Set up permissions** - Configure who can execute which commands [📖 Permissions Setup Guide](./permissions-setup-guide.md)

2. **Monitor usage** - Review command logs for performance and security
3. **Enable debug logging** for troubleshooting (optional) [🐛 Debug Logging Guide](./debug-logging.md)
