# Plugin Upgrade

This guide explains how to upgrade the NetBox Toolkit Plugin to a newer version.

## Upgrade Process

### 1. **Activate Virtual Environment**

```bash
source /opt/netbox/venv/bin/activate
```

### 2. **Upgrade the Plugin**

```bash
pip install --upgrade netbox-toolkit-plugin
```

### 3. **Apply Database Migrations**

Apply any new database migrations that come with the updated version:

```bash
cd /opt/netbox/netbox
python3 manage.py migrate netbox_toolkit_plugin
```

### 4. **Collect Static Files**

Update static files (CSS, JavaScript) to ensure new features display correctly:

```bash
python3 manage.py collectstatic --no-input
```

### 5. **Restart NetBox Services**

Restart NetBox to load the new version:

```bash
sudo systemctl restart netbox netbox-rq
```



## Getting Help

If you encounter issues during upgrade:

1. Check the [Changelog](../changelog.md) for known issues
2. Review [GitHub Issues](https://github.com/bonzo81/netbox-toolkit-plugin/issues)
3. Ask in [GitHub Discussions](https://github.com/bonzo81/netbox-toolkit-plugin/discussions)
