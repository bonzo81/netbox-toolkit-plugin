# NetBox Command Toolkit Plugin

> ⚠️ **EARLY DEVELOPMENT WARNING** ⚠️  
> This plugin is in very early development and not recommended for production use. There will be bugs and possible incomplete functionality. Use at your own risk! If you do, give some feedback in [Discussions](https://github.com/bonzo81/netbox-toolkit-plugin/discussions)

A NetBox plugin that allows you to run commands on network devices directly from the device page. 



### 📋 Feature Overview
- **🔧 Command Creation**: Define platform-specific commands (show/config types)
- **🔐 Command Permissions**: Granular access control using NetBox's permission system
- **⚡ Command Execution**: Run commands directly from device pages via "Toolkit" tab
- **📄 Raw Output**: View complete, unfiltered command responses
- **🔍 Parsed Output**: Automatic JSON parsing using textFSM templates
- **📊 Command Logs**: Complete execution history with timestamps
- **🐛 Debug Logging**: Optional detailed logging for troubleshooting


### Built with:
- Scrapli for device connections
- Netmiko as a fallback for problematic devices
- TextFSM for structured data parsing

### Created with:
- VSCode
- Copilot
- RooCode

>   This project is a work in progress and in early development. It is not recommended for production use. Feedback and contributions are welcome!

## 📚 Essential Guides

#### 🚀 Getting Started
- [📦 Installation](./docs/user/installation.md) - Install the plugin in your NetBox environment
- [⚙️ Configuration](./docs/user/configuration.md) - Configure plugin settings and options

#### 📋 Command Management  
- [📋 Command Creation](./docs/user/command-creation.md) - Create platform-specific commands
- [🔐 Permissions Setup](./docs/user/PERMISSIONS_SETUP_GUIDE.md) - Configure granular access control
- [📝 Permission Examples](./docs/user/permission-examples.md) - Example permission configuration

#### 🔧 Troubleshooting
- [🐛 Debug Logging](./docs/user/debug-logging.md) - Enable detailed logging for debugging


## Contributing

**🚀 Want to Contribute?** Start with the [Contributor Guide](./docs/contributing.md) for a fast overview of the codebase.


## Future ideas:
- Enhance API to allow execution of commands and return either parsed or raw data.
- Enable variable use in the command creation and execution, based on device attributes.

