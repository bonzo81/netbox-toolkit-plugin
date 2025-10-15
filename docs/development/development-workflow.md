# Development Workflow

Follow this step-by-step process to contribute code changes to the NetBox Toolkit Plugin.

## Development Environment Options

### 🚀 Using Dev Container (Recommended)
If you're using the dev container, many setup steps are automated:

- ✅ Environment setup is complete after container starts
- ✅ Plugin is automatically installed in development mode
- ✅ Database migrations are applied automatically
- ✅ NetBox server starts automatically
- 🔄 Use `netbox-reload` instead of manual `pip install -e .`
- 🔄 Use `netbox-restart` for server management
- 🔄 Use `netbox-logs` to view server output

**📖 Dev Container Details**: See `.devcontainer/README.md` in the project root for configuration options.

### 🛠️ Traditional Development Setup
For manual environment setup, follow the complete guide: **[Development Setup](setup.md)**

## 1. Environment Setup

Follow the complete setup guide: **[Development Setup](setup.md)**

## 2. Create a Branch for Development

**For Develop Branch Development:**

```bash
git checkout develop
git pull upstream develop
git checkout -b feature/your-feature-name
```

## 3. Make Your Changes

**Using Dev Container:**
```bash
# Make your changes locally (files are automatically synced)
# Edit files...

# If you changed package structure, reinstall plugin
netbox-reload

# Migrations are applied automatically on restart
# Or apply manually if needed:
cd /opt/netbox/netbox
python manage.py migrate netbox_toolkit_plugin
```

**Traditional Development:**
```bash
# Make your changes locally
# Edit files...

# If you changed package structure, reinstall
pip install -e .

# Apply any new migrations
cd /opt/netbox/netbox
python manage.py migrate netbox_toolkit_plugin
```

## 4. Test Your Changes

**Using Dev Container:**
```bash
# NetBox is already running at http://localhost:8000
# Test your changes in the browser
# Check logs for any issues
netbox-logs

# Run tests and linting
netbox-test
ruff-check .
```

**Traditional Development:**
```bash
# Run NetBox development server
cd /opt/netbox/netbox
python manage.py runserver 0.0.0.0:8000

# Test your changes in the browser
# Check logs for any issues

# Run tests and linting
python -m pytest
ruff check .
```

## 5. Commit and Push Changes

```bash
git add .
git commit -m "Your detailed description of your changes."
git push origin name-of-your-bugfix-or-feature
```

## 6. Submit a Pull Request

After pushing to your fork:

1. **Navigate to your fork** on GitHub (e.g., `https://github.com/yourusername/netbox-toolkit-plugin`)
2. **GitHub will often show a banner** suggesting to create a pull request for your recently pushed branch
3. **Click "Compare & pull request"** or go to the "Pull requests" tab and click "New pull request"
4. **Ensure the base repository is set correctly:**
     - Base repository: `bonzo81/netbox-toolkit-plugin`
     - Base branch: `develop` (for new features) or `main` (for hotfixes)
     - Head repository: `yourusername/netbox-toolkit-plugin`
     - Compare branch: `feature/your-feature-name`
5. **Fill out the pull request template** with details about your changes
6. **Submit the pull request**

### Important Notes:

- Pull requests are **NOT created automatically** - you must create them manually
- Your changes go to **your fork first**, then you request they be pulled into the main repository
- For new features, target the **`develop` branch**
- For bug fixes on released versions, target the **`main` branch**