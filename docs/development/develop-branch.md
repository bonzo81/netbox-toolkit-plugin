# Using the Develop Branch

The `develop` branch contains the latest development features and fixes that are being prepared for the next release. This guide explains how to install, test, and contribute to the develop branch.

## ⚠️ Important Considerations

- **Not for Production**: The develop branch is unstable and should never be used in production environments
- **Breaking Changes**: Features may change or be removed between commits
- **Database Migrations**: Development migrations may change, requiring database resets
- **Active Development**: Code is actively changing and may contain bugs


### 1. Fork the Repository

Fork the 'netbox-toolkit-plugin' repo on GitHub.

### 2. Clone the Repository

Clone your forked repository locally:

```bash
git clone git@github.com:<username>/netbox-toolkit-plugin.git
cd netbox-toolkit-plugin

# Add upstream remote to sync with main repo
git remote add upstream https://github.com/bonzo81/netbox-toolkit-plugin.git

# Switch to develop branch
git checkout develop
```

### 3. Install Plugin for Development

```bash
# Install in development mode
pip install -e .

# Apply database migrations
cd /opt/netbox/netbox
python manage.py migrate netbox_toolkit_plugin
```

## Development Workflow

### 1. Create Feature Branch

```bash
# Start from updated develop branch
git checkout develop
git pull upstream develop

# Create feature branch
git checkout -b feature/your-feature-name
```

### 2. Make Changes

```bash
# Make your changes
# Edit files...

# If you changed package structure, reinstall
pip install -e .

# Apply any new migrations
python manage.py migrate netbox_toolkit_plugin
```

### 3. Test Changes

```bash
# Run NetBox development server
cd /opt/netbox/netbox
python manage.py runserver 0.0.0.0:8000

# Test your changes in the browser
# Check logs for any issues
```

### 4. Submit Pull Request

```bash
# Push to your fork
git push origin feature/your-feature-name

# Create pull request on GitHub targeting the develop branch
```

