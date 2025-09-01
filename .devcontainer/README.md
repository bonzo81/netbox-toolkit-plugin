# NetBox Toolkit Plugin - Development Container

This directory contains the development container configuration for the NetBox Toolkit Plugin. It provides a complete development environment using the official NetBox Docker images with PostgreSQL and Redis.

## 🚀 Quick Start

1. **Open in VS Code**: Open the project in VS Code and click "Reopen in Container" when prompted, or run `Ctrl+Shift+P` → "Dev Containers: Reopen in Container"

2. **Wait for setup**: The container will automatically install your plugin and set up the development environment (this may take a few minutes on first run)

3. **NetBox auto-starts**: After setup completes, NetBox will automatically start in the background

4. **Access NetBox**: Open http://localhost:8000 in your browser (may take a moment to be ready)
   - Username: `admin`
   - Password: `admin`

## 🔧 Configuration

### NetBox Version

You can specify which NetBox Docker image version to use by setting the `NETBOX_VERSION` environment variable:

```bash
# Set in your shell before opening the devcontainer
export NETBOX_VERSION=v4.1-3.3.0
```

Or modify the `NETBOX_VERSION` value in `.devcontainer/devcontainer.json`.

Available image tags:
- `latest` (default) - Latest stable NetBox release
- `v4.1-3.3.0` - NetBox v4.1 with NetBox Docker v3.3.0
- `v4.0-3.3.0` - NetBox v4.0 with NetBox Docker v3.3.0
- `snapshot` - Latest development version
- See [Docker Hub](https://hub.docker.com/r/netboxcommunity/netbox/tags) for all available tags

### Environment Variables

The devcontainer supports these environment variables (set in `.env` or your shell environment):

#### **Core Configuration**
- `NETBOX_VERSION`: NetBox Docker image tag (default: `latest`)
  - Available: `latest`, `v4.1-3.3.0`, `v4.0-3.3.0`, `snapshot`
  - See [Docker Hub](https://hub.docker.com/r/netboxcommunity/netbox/tags) for all tags

- `DEBUG`: Enable Django debug mode (default: `True`)
  - Set to `False` for production-like testing

- `SECRET_KEY`: Django secret key (default: development key)
  - Must be 50+ characters for production use

#### **Database Configuration**
- `DB_HOST`: PostgreSQL server hostname (default: `postgres`)
- `DB_NAME`: Database name (default: `netbox`)
- `DB_USER`: Database username (default: `netbox`)
- `DB_PASSWORD`: Database password (default: `netbox`)

#### **Redis Configuration**
- `REDIS_HOST`: Redis server hostname (default: `redis`)
- `REDIS_PASSWORD`: Redis password (default: empty)

#### **Superuser Configuration**
These control the automatic creation of the admin user:
- `SUPERUSER_NAME`: Admin username (default: `admin`)
- `SUPERUSER_EMAIL`: Admin email (default: `admin@example.com`)
- `SUPERUSER_PASSWORD`: Admin password (default: `admin`)
- `SKIP_SUPERUSER`: Skip automatic superuser creation (default: `false`)

#### **Using Environment Variables**

**Option 1: Create .env file** (recommended for persistent settings):
```bash
# Copy the example and customize
cp .devcontainer/.env.example .devcontainer/.env
# Edit .devcontainer/.env with your preferred values
```

**Option 2: Set in shell** (for temporary changes):
```bash
export NETBOX_VERSION=v4.1-3.3.0
export DB_PASSWORD=mypassword
# Then open the devcontainer
```

**Option 3: VS Code settings** (per-workspace):
```json
// In .vscode/settings.json
{
    "terminal.integrated.env.linux": {
        "NETBOX_VERSION": "v4.1-3.3.0",
        "DEBUG": "False"
    }
}
```

#### **Advanced Configuration**

For NetBox application settings (not infrastructure), use the configuration file approach instead of environment variables:

- `TIME_ZONE`, banner settings, logging configuration → use `extra-configuration.py`
- Plugin-specific settings → use `PLUGINS_CONFIG` in `extra-configuration.py`
- Authentication backends → use `extra-configuration.py`

See the "Extra NetBox Configuration" section below for details.

## 📋 Available Commands

The setup script creates these convenient aliases:

**NetBox Management:**
- `netbox-start`: Start NetBox in background
- `netbox-run`: Start NetBox in foreground (for debugging)
- `netbox-stop`: Stop background NetBox server
- `netbox-restart`: Restart NetBox (stop + start)
- `netbox-reload`: Reinstall plugin and restart NetBox
- `netbox-status`: Check if NetBox is running
- `netbox-logs`: View NetBox server logs
- `netbox-shell`: Open the NetBox Django shell
- `netbox-manage`: Run Django management commands

**Development:**
- `netbox-test`: Run plugin tests
- `plugin-install`: Reinstall plugin in development mode
- `ruff-check`: Check code with Ruff
- `ruff-format`: Format code with Ruff
- `ruff-fix`: Auto-fix code issues with Ruff

## 🐘 Services

The development environment includes:

- **NetBox**: Official NetBox Docker image on port 8000
- **PostgreSQL 15**: Database server
- **Redis 7**: Cache and message broker

## 📁 Directory Structure

```
.devcontainer/
├── devcontainer.json       # Main devcontainer configuration
├── docker-compose.yml      # Services configuration
├── setup.sh               # Post-creation setup script
├── start-netbox.sh        # NetBox startup script (auto-generated)
├── .env.example           # Environment variables template
└── README.md              # This file
```

## 🔄 Development Workflow

1. **Make changes** to your plugin code in the main directory
2. **NetBox auto-reloads** for most changes (Django development server)
3. **For plugin changes**: Use `netbox-reload` to reinstall and restart
4. **For quick restart**: Use `netbox-restart` without reinstalling
5. **Test your changes** using `netbox-test`
6. **Debug** using `netbox-shell` for Django shell access or VS Code debugger
7. **View logs** with `netbox-logs` to see server output

## 🐛 Troubleshooting

### Container won't start
- Ensure Docker is running
- Try rebuilding the container: `Ctrl+Shift+P` → "Dev Containers: Rebuild Container"

### NetBox won't start
- Check if PostgreSQL and Redis are running: `docker-compose ps`
- View logs: `docker-compose logs postgres redis devcontainer`
- Check NetBox logs: `netbox-logs`
- Check NetBox status: `netbox-status`
- Try restarting: `netbox-restart`

### Migration errors
If you see import errors during database migration:
- The setup script adds plugin configuration directly to NetBox's main configuration
- If migration fails, try rebuilding the container: `Ctrl+Shift+P` → "Dev Containers: Rebuild Container"
- Check that plugin configuration was added: `cat /etc/netbox/config/configuration.py | grep toolkit`

### SECRET_KEY errors
If you see "SECRET_KEY must be at least 50 characters" error:
- The devcontainer sets a development SECRET_KEY automatically
- If the error persists, rebuild the container: `Ctrl+Shift+P` → "Dev Containers: Rebuild Container"
- The SECRET_KEY is set in both `devcontainer.json` and `docker-compose.yml`

### Plugin not loading
- Ensure the plugin is installed: `uv pip install -e .` or `plugin-install`
- Check if plugin configuration exists: `cat /etc/netbox/config/configuration.py | grep toolkit`
- Restart NetBox server: `netbox-restart` or `netbox-reload`

### Database issues
- Reset database: Stop services, run `docker-compose down -v`, then restart

### Permission issues
- The devcontainer runs as root to avoid permission issues
- Plugin files should be accessible from `/workspaces/netbox-toolkit-plugin`

## 🔧 Customization

### Adding Extra Plugins and Configuration

You can extend the development environment by adding optional configuration files to the `.devcontainer` folder:

#### Extra Python Packages
Create `.devcontainer/extra-requirements.txt` to install additional Python packages:
```txt
netbox-secrets>=1.9.0
netbox-topology-views>=3.8.0
django-debug-toolbar>=4.0.0
```

#### Extra NetBox Plugins
Create `.devcontainer/extra-plugins.py` to add additional NetBox plugins:
```python
# Add additional plugins to the PLUGINS list
PLUGINS.extend([
    'netbox_secrets',
    'netbox_topology_views',
])

# Configure additional plugins
PLUGINS_CONFIG.update({
    'netbox_secrets': {
        'apps': ['dcim', 'ipam'],
    },
})
```

#### Extra NetBox Configuration
Create `.devcontainer/extra-configuration.py` to add custom NetBox settings:
```python
# Custom time zone
TIME_ZONE = 'America/New_York'

# Custom banner
BANNER_TOP = 'Development Environment'

# Custom logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    # ... your logging config
}
```

**Example files** are provided with `.example` extensions that you can copy and customize.

### Legacy Configuration Methods
- Plugin configuration is in `/etc/netbox/config/plugins.py`
- Main NetBox config is in `/etc/netbox/config/configuration.py`

### VS Code extensions
Add extensions to the `customizations.vscode.extensions` array in `devcontainer.json`.

## 🏗️ Using Official NetBox Docker

This devcontainer now uses the official [NetBox Docker images](https://github.com/netbox-community/netbox-docker) which provides:

- ✅ Pre-configured NetBox installation
- ✅ Proper Python virtual environment setup
- ✅ All NetBox dependencies included
- ✅ Production-like environment structure
- ✅ Automated superuser creation
- ✅ Persistent data volumes

## 📚 Resources

- [NetBox Documentation](https://docs.netbox.dev/)
- [NetBox Plugin Development](https://docs.netbox.dev/en/stable/plugins/development/)
- [NetBox Docker Repository](https://github.com/netbox-community/netbox-docker)
- [Dev Containers Documentation](https://containers.dev/)
