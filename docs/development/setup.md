# Development Setup

This guide will help you set up a development environment for working on the NetBox Toolkit Plugin.



💡 **Tip**: Start with the [Contributing Guide](./contributing.md) for the complete development workflow and overview.

## Setting Up a Development Environment

### 1. Fork the Repository

Fork the 'netbox-toolkit-plugin' repo on GitHub.

### 2. Clone the Repository

Clone your forked repository locally:

```
$ git clone git@github.com:<username>/netbox-toolkit-plugin.git
```

### 3. Create a Virtual Environment

Activate the NetBox virtual environment (see the NetBox documentation under [Setting up a Development Environment](https://docs.netbox.dev/en/stable/development/getting-started/)):

```
$ source /opt/netbox/venv/bin/activate
```

### 4. Install plugin in Develop Mode

Add the plugin to NetBox virtual environment in Develop mode (see [Plugins Development](https://docs.netbox.dev/en/stable/plugins/development/)):

To ease development, it is recommended to go ahead and install the plugin at this point using setuptools' `develop` mode. This will create symbolic links within your Python environment to the plugin development directory. Call `pip` from the plugin's root directory with the `-e` flag:


```
$ pip install -e .
```

### 5. Apply Migrations

```bash
cd /opt/netbox/netbox
python manage.py migrate netbox_toolkit
```

### 6. Collect Static Files

```bash
cd /opt/netbox/netbox
python manage.py collectstatic --no-input
```


### 7. Create a branch for local development:

```
$ git checkout -b name-of-your-bugfix-or-feature
```

Now you can make your changes locally.

### 8. Commit your changes and push your branch to GitHub:

```
$ git add .
$ git commit -m "Your detailed description of your changes."
$ git push origin name-of-your-bugfix-or-feature
```

### 9. Submit a pull request through the GitHub website.


## Pull Request Guidelines

Before you submit a pull request, check that it meets these guidelines:

1. Ideally the pull request should include tests.
2. If the pull request adds functionality, the docs should be updated. Put
   your new functionality into a function with a docstring, and add the
   feature to the list in README.md.
3. The pull request should work for Python 3.10+. Check
   https://github.com/bonzo81/netbox-librenms-plugin/actions
   and make sure that the tests pass for all supported Python versions.


## Deploying

A reminder for the maintainers on how to deploy.
Make sure all your changes are committed (including an entry in changelog.md) and that all tests pass.
Then in the github project go to `Releases` and create a new release with a new tag.  This will automatically upload the release to pypi:
