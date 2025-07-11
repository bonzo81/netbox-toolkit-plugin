# Development Setup

This guide will help you set up a development environment for working on the NetBox Toolkit Plugin.



💡 **Tip**: Start with the [Contributing Guide](./contributing.md) for the complete development workflow and overview.

## Setting Up a Development Environment

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

## Development Workflow

### 8. Create a branch for local development:


**For Develop Branch Development:**
```bash
$ git checkout develop
$ git pull upstream develop
$ git checkout -b feature/your-feature-name
```

### 9. Make Your Changes

```bash
# Make your changes locally
# Edit files...

# If you changed package structure, reinstall
$ pip install -e .

# Apply any new migrations
$ cd /opt/netbox/netbox
$ python manage.py migrate netbox_toolkit_plugin
```

### 10. Test Your Changes

```bash
# Run NetBox development server
$ cd /opt/netbox/netbox
$ python manage.py runserver 0.0.0.0:8000

# Test your changes in the browser
# Check logs for any issues
```

### 11. Commit your changes and push your branch to GitHub:

```
$ git add .
$ git commit -m "Your detailed description of your changes."
$ git push origin name-of-your-bugfix-or-feature
```

### 12. Submit a pull request through the GitHub website

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

**Important Notes:**
- Pull requests are **NOT created automatically** - you must create them manually
- Your changes go to **your fork first**, then you request they be pulled into the main repository
- For new features, target the **`develop` branch**
- For bug fixes on released versions, target the **`main` branch**


## Deploying

A reminder for the maintainers on how to deploy.
Make sure all your changes are committed (including an entry in changelog.md) and that all tests pass.
Then in the github project go to `Releases` and create a new release with a new tag.  This will automatically upload the release to pypi:
