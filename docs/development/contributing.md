# Contributing

Contributions are welcome, and they are greatly appreciated! Every little bit
helps, and credit will always be given.

We love your input! We want to make contributing to this project as easy and transparent as possible, whether it's:


## Contribution Types

### 🐛 Bug Fixes
- Check existing issues first
- Include reproduction steps
- Add tests if possible
- Report bugs at https://github.com/bonzo81/netbox-toolkit-plugin/issues.

### ✨ New Features  
- Discuss major changes in issues first
- Follow existing patterns
- Update documentation
- Use the develop branch for latest features (see [Development Setup](./setup.md))

### 📚 Documentation
- Improve clarity and examples
- Fix typos and formatting
- Add missing information

### 🧪 Testing
- Add test coverage
- Improve existing tests
- Add integration tests

## 🚀 Development Workflow

For detailed development setup and workflow, see:
- **[Development Setup](./setup.md)** - Complete environment setup including develop branch usage
- **[Code Guide](./code-guide.md)** - Navigate the codebase

### Submit Feedback

The best way to send feedback is to file an issue at https://github.com/bonzo81/netbox-toolkit-plugin/issues.

If you are proposing a feature:

* Explain in detail how it would work.
* Keep the scope as narrow as possible, to make it easier to implement.
* Remember that this is a volunteer-driven project, and that contributions
  are welcome :)


### Core Principles
✅ **Platform-Based**: Commands tied to NetBox platforms (cisco_ios, cisco_nxos)  
✅ **Service Layer**: Business logic isolated in dedicated service classes  
✅ **Connector Abstraction**: Uniform interface for all device connections  
✅ **Permission Integration**: Leverages NetBox's ObjectPermission system  
✅ **Scrapli-First**: Primary network library with fallback support  



## 📦 Key Dependencies

### Primary Libraries
- **Scrapli** - Network device connections (SSH/Telnet/NETCONF)
- **Scrapli-Community** - Extended platform support  
- **Netmiko** - SSH fallback for problematic devices
- **TextFSM** - Structured data parsing

### NetBox Integration
- Uses NetBox's `Platform` model (not `DeviceType`)
- Leverages `ObjectPermission` for access control
- Integrates via custom `ViewTab` system

## 💬 Getting Help

- **Issues**: Report bugs and feature requests
- **Discussions**: Ask questions and get help
- **Code Review**: Submit pull requests for feedback

**Thank you for contributing! 🎉**
