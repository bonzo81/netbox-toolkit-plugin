# Getting Started

This guide will help you get started with the NetBox Toolkit Plugin after installation.

## Overview

The NetBox Toolkit Plugin allows you to:

1. Define reusable commands for network devices
2. Execute commands on devices directly from the NetBox interface
3. View command outputs and execution logs
4. Organize commands by device platform

## First Steps

### 1. Access the Plugin

After installation, you can access the plugin from the NetBox navigation menu:

1. Log in to your NetBox instance
2. Click on the "Plugins" dropdown in the navigation bar
3. Select "Toolkit" from the menu

### 2. Define Commands

Before executing commands on devices, you need to define the commands:

1. Navigate to Plugins > Toolkit > Commands
2. Click "Add" to create a new command
3. Fill in the command details:
   - **Name**: A descriptive name (e.g., "Show Interface Status")
   - **Command**: The actual command to execute
     - Simple: `show version`
     - With variables: `show interface <interface_name> status`
   - **Description**: Optional explanation of what the command does
   - **Platform**: The device platform this command is designed for (e.g., `cisco_ios`, `cisco_nxos`, `arista_eos`)
   - **Command Type**: Categorize the command (Show, Configuration, Diagnostic, etc.)
   - **Tags**: Optional tags for better organization

4. **Add Variables (if needed)**: If your command includes `<variable_name>` syntax, define each variable with appropriate types and validation

5. Click "Create" to save the command

> 📚 **Need more details?** See the [Command Creation Guide](./command-creation.md) for detailed information about variable syntax, types, and troubleshooting.

### 3. Execute Commands on Devices

To execute commands on a device:

1. Navigate to the device's detail page in NetBox
2. Click on the "Toolkit" tab
3. Select a command from the dropdown
4. **Fill in variables** (if the command has any): The form will show dropdowns/fields for each variable
5. Enter your device credentials
6. Click "Execute" to run the command
6. View the command output on the page

### 4. View Command Logs

To view the history of executed commands:

1. Navigate to Plugins > Toolkit > Command Logs
2. Browse the list of executed commands
3. Click on a log entry to view details including:
   - Command executed
   - Device
   - Timestamp
   - User who executed the command
   - Command output or error message

## Creating Useful Commands

Here are some examples of useful commands for different platforms:

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

## Platform Support

The plugin supports various network device platforms including:

- Cisco IOS/IOS-XE (`cisco_ios`)
- Cisco NX-OS (`cisco_nxos`)
- Cisco IOS-XR (`cisco_iosxr`)
- Juniper Junos (`juniper_junos`)
- Arista EOS (`arista_eos`)

When creating commands, make sure to select the appropriate platform to ensure compatibility.

## Best Practices

### Security Considerations

- Use read-only credentials when possible
- Consider using AAA on your network devices to limit command access
- Monitor command logs for unauthorized access
- Be cautious with configuration commands that might disrupt network operations

### Command Organization

- Create descriptive names for commands
- Group related commands with consistent naming conventions
- Add detailed descriptions to explain command purpose and output
- Use platform-specific commands rather than generic ones for better results

### Performance Considerations

- Avoid executing resource-intensive commands during peak hours
- Set appropriate timeouts for commands that might take longer to execute
- Consider the impact of commands on device CPU and memory

## Next Steps

Once you're familiar with basic command execution, you can:

1. Create more complex commands for your specific needs
2. Organize commands by platform and function
3. Explore the plugin's API for programmatic access
4. Integrate command execution into your network operations workflows

For more details, see the plugin documentation.
