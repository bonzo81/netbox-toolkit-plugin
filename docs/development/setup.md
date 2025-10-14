# Development Setup

This guide will help you set up a development environment for working on the NetBox Toolkit Plugin.



💡 **Tip**: Start with the [Contributing Guide](index.md) for the complete development workflow and overview.

After setting up your environment, follow the **[Development Workflow](development-workflow.md)** for the complete step-by-step contribution process.

## Setting Up a Development Environment

### 🚀 Quick Start with Dev Container (Recommended)

The fastest way to get started is using the pre-configured development container, which includes NetBox, PostgreSQL, Redis, and all development tools.

**Prerequisites**: Docker and VS Code with the "Dev Containers" extension.

1. **Open in Dev Container**:
   ```bash
   # Option 1: Open in VS Code
   # - Open the project in VS Code
   # - When prompted, click "Reopen in Container"
   # - Or use Ctrl+Shift+P → "Dev Containers: Reopen in Container"
   ```

2. **Wait for Setup**: The container automatically:
   - Installs the plugin in development mode
   - Sets up PostgreSQL and Redis
   - Creates a superuser account (`admin`/`admin`)
   - Starts NetBox on http://localhost:8000

3. **Start Developing**: NetBox is now running and ready for development!

**💡 Dev Container Benefits:**

- ✅ Complete environment in minutes
- ✅ All dependencies pre-installed
- ✅ Consistent across different machines
- ✅ Includes development tools (Ruff, Python extensions)
- ✅ Works with GitHub Codespaces

**📖 Learn more**: See `.devcontainer/README.md` in the project root for advanced configuration options.

---

### 🛠️ Traditional Development Setup

If you prefer manual setup or need more control over your environment, follow these steps:

### 1. Fork the Repository

Fork the 'netbox-toolkit-plugin' repo on GitHub.

### 2. Clone the Repository

Clone your forked repository locally:

```bash
$ git clone git@github.com:<username>/netbox-toolkit-plugin.git
$ cd netbox-toolkit-plugin

# Add upstream remote to sync with main repo
$ git remote add upstream https://github.com/bonzo81/netbox-toolkit-plugin.git
```

### 3. Select develop Branch

```bash
$ git checkout develop
```

⚠️ **Develop Branch Considerations:**

- Contains latest development features and fixes
- **Not for Production**: Unstable and may contain breaking changes
- **Database Migrations**: Development migrations may change, requiring resets
- **Active Development**: Code is actively changing and may contain bugs

### 4. Create a Virtual Environment

Activate the NetBox virtual environment (see the NetBox documentation under [Setting up a Development Environment](https://docs.netbox.dev/en/stable/development/getting-started/)):

```
$ source /opt/netbox/venv/bin/activate
```

### 5. Install plugin in Develop Mode

Add the plugin to NetBox virtual environment in Develop mode (see [Plugins Development](https://docs.netbox.dev/en/stable/plugins/development/)):

To ease development, it is recommended to go ahead and install the plugin at this point using setuptools' `develop` mode. This will create symbolic links within your Python environment to the plugin development directory. Call `pip` from the plugin's root directory with the `-e` flag:


```
$ pip install -e .
```

### 6. Apply Migrations

```bash
cd /opt/netbox/netbox
python manage.py migrate netbox_toolkit
```

### 7. Collect Static Files

```bash
cd /opt/netbox/netbox
python manage.py collectstatic --no-input
```

## 🚀 Next Steps

Now that your development environment is set up, you're ready to start contributing!

**Continue with the [Development Workflow](development-workflow.md) to learn how to:**

- Create feature branches
- Make and test changes
- Submit pull requests
- Follow contribution best practices

The workflow guide provides the complete step-by-step process for contributing to the NetBox Toolkit Plugin.
