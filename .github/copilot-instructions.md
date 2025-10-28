# NetBox Toolkit Plugin - AI Coding Agent Instructions

A NetBox plugin for secure network device command execution with multi-platform support, encrypted credential storage, and comprehensive logging.

## Development Environment

**Dev Container (Recommended)**: `.devcontainer/` provides complete NetBox+PostgreSQL+Redis environment

```bash
# Quick start commands (auto-aliased in dev container)
netbox-start          # Start NetBox in background
netbox-run            # Start in foreground (see logs)
netbox-restart        # Restart server
netbox-reload         # Reinstall plugin + restart (after code changes)
netbox-logs           # View server logs
netbox-stop           # Stop server

# Access: http://localhost:8000 (admin/admin)
# GitHub Codespaces: Auto-detects and shows correct URL
```

**Manual Setup**: See `docs/development/setup.md` for traditional environment setup

## Tech Stack & Critical Dependencies

- **Scrapli**: Primary network device SSH library (high-performance, structured)
- **Netmiko**: Fallback SSH client (legacy device compatibility)
- **Scrapli-Community**: Extended platform support
- **Tabler CSS**: NetBox's framework (NOT Bootstrap)
- **Argon2id**: Credential encryption (via `argon2-cffi`)
- **Fernet**: AES-128 encryption for stored credentials (via `cryptography`)

## Core Architecture

### Connector Factory Pattern with Fast-Fail Fallback
```python
# Smart connector creation: Scrapli primary → Netmiko fallback
connector = ConnectorFactory.create_connector(
    device=device,
    username=credentials["username"],
    password=credentials["password"],
    use_fallback=True  # Enables automatic fallback
)

# Platform normalization (ALWAYS use this)
platform = ToolkitSettings.normalize_platform(device.platform.slug)
# "ios-xe" → "cisco_ios", "nxos" → "cisco_nxos", etc.
```

**Fallback Logic**: `factory.py` tries Scrapli first, falls back to Netmiko on socket errors, timeouts, or unsupported platforms. See `CONNECTOR_MAP` for platform-specific overrides (e.g., `hp_procurve` → direct Netmiko).

### Service Layer (Business Logic Isolation)
- `CommandExecutionService`: Orchestrates command execution, retry logic, rate limiting
- `DeviceService`: Device validation, connection info, platform compatibility
- `CredentialService`: Token-based credential management (hash-based tokens, not JWTs)
- `EncryptionService`: Argon2-based credential encryption/decryption
- `RateLimitingService`: Execution throttling (per-device, per-user)

### Service Layer (Business Logic Isolation)
- `CommandExecutionService`: Orchestrates command execution, retry logic, rate limiting
- `DeviceService`: Device validation, connection info, platform compatibility
- `CredentialService`: Token-based credential management (hash-based tokens, not JWTs)
- `EncryptionService`: Argon2-based credential encryption/decryption
- `RateLimitingService`: Execution throttling (per-device, per-user)

### Models & Key Relationships

**Command**: Multi-platform command definitions
```python
platforms = ManyToManyField('dcim.Platform')  # NOT ForeignKey
command_type = CharField(choices=[('show', 'Show Command'), ('config', 'Configuration Command')])
variables = RelatedManager  # CommandVariable objects
```

**CommandVariable**: Dynamic command parameters with `<variable_name>` syntax
```python
variable_type = CharField  # 'interface', 'vlan', 'ip_address', 'text'
required = BooleanField
default_value = CharField(blank=True)
# Usage in commands: "show interface <interface_name> status"
```

**DeviceCredentialSet**: Encrypted credentials with custom manager
```python
owner = ForeignKey('users.User')
platforms = ManyToManyField('dcim.Platform', blank=True)  # Optional platform filtering
encrypted_username/password = TextField  # Fernet encrypted
access_token = CharField(unique=True)  # Argon2 hash for API access

# Custom manager with platform filtering
objects = DeviceCredentialSetManager()
credentials = DeviceCredentialSet.objects.for_user_and_device(user, device)
```

**CommandLog**: Immutable audit records (view/delete only, no add/change)
```python
class Meta:
    default_permissions = ('view', 'delete')  # Audit trail pattern
```

## NetBox Plugin Integration

### Device Tab Registration
```python
# views/device_views.py
@register_model_view(Device, name='toolkit', path='toolkit')
class DeviceToolkitView(generic.ObjectView):
    tab = ViewTab(label='Toolkit')
    # Adds custom tab to NetBox device pages
```

### Permission System
```python
# Models use NetBox's ObjectPermission system
class Meta:
    permissions = [
        ('execute_show', 'Can execute show commands'),
        ('execute_config', 'Can execute configuration commands'),
    ]

# Check permissions in views/services
from utilities.permissions import get_permission_for_model
permission = get_permission_for_model(Command, 'execute_show')
user.has_perm(permission)

# Filter objects by permissions
from guardian.shortcuts import get_objects_for_user
commands = get_objects_for_user(user, 'netbox_toolkit_plugin.execute_show', klass=Command)
```

### URL Patterns
All plugin URLs use namespace: `plugins:netbox_toolkit_plugin:*`
```python
# Example reversals
reverse('plugins:netbox_toolkit_plugin:command_list')
reverse('plugins:netbox_toolkit_plugin:command_detail', kwargs={'pk': pk})
```

## Configuration System (`settings.py`)

**Platform Normalization** (single source of truth):
```python
ToolkitSettings.normalize_platform("ios-xe")  # → "cisco_ios"
ToolkitSettings.normalize_platform("nxos")    # → "cisco_nxos"
```

**Security Configuration** (REQUIRED pepper):
```python
# In NetBox's configuration.py
PLUGINS_CONFIG = {
    'netbox_toolkit_plugin': {
        'security': {
            'pepper': 'your-generated-pepper-here',  # REQUIRED (48+ chars)
        },
    },
}

# Or via environment variable
NETBOX_TOOLKIT_PEPPER='your-pepper-here'

# Generate pepper:
# python -c "import secrets; print(secrets.token_urlsafe(48))"
```

**Device-Specific Timeouts**:
```python
ToolkitSettings.get_timeouts_for_device("WS-C6509-E")  # Catalyst-specific
ToolkitSettings.DEVICE_TIMEOUTS['catalyst']  # Override defaults
```

## Development Workflows

### Testing & Linting (VS Code Tasks)
```bash
# Run all tests
# Task: "Run Plugin Tests" (pytest in NetBox context)

# Connector-specific tests
# Task: "Run Connector Tests"

# Code quality
# Task: "Ruff: Check Python Code"
# Task: "Ruff: Format & Fix All"
```

### Making Changes
1. Edit code in `/workspaces/netbox-toolkit-plugin/netbox_toolkit_plugin/`
2. If package structure changed: `netbox-reload` (reinstall + restart)
3. If only code changed: `netbox-restart` (reload server)
4. For migrations: `cd /opt/netbox/netbox && python manage.py makemigrations netbox_toolkit_plugin`

### Plugin Registration (`__init__.py`)
```python
class ToolkitPluginConfig(PluginConfig):
    name = "netbox_toolkit_plugin"
    base_url = "toolkit"
    min_version = "4.2.0"  # Minimum NetBox version
    
    def ready(self):
        # Validates pepper configuration at startup
        ToolkitSettings.get_security_config()
```

## Variable Substitution Pattern

**Command Text Syntax**: Use `<variable_name>` (NOT Django `{{ variable_name }}`)
```python
# utils/variable_parser.py
CommandVariableParser.extract_variables("show interface <interface_name> status")
# Returns: ['interface_name']

CommandVariableParser.substitute_variables(
    "show interface <interface_name>",
    {"interface_name": "GigabitEthernet0/1"}
)
# Returns: "show interface GigabitEthernet0/1"
```

## Platform Support Matrix

| Platform | Primary | Fallback | Notes |
|----------|---------|----------|-------|
| cisco_ios | Scrapli | Netmiko | All IOS/IOS-XE variants |
| cisco_nxos | Scrapli | Netmiko | NX-OS 9k/7k/5k/3k |
| cisco_iosxr | Scrapli | Netmiko | IOS-XR devices |
| juniper_junos | Scrapli | Netmiko | All Junos platforms |
| arista_eos | Scrapli | Netmiko | All EOS versions |
| hp_procurve | Netmiko | - | Direct Netmiko (legacy) |
| paloalto_panos | Netmiko | - | Direct Netmiko (specialized) |

See `connectors/factory.py` → `CONNECTOR_MAP` for complete list.

## Common Pitfalls ❌

- **Don't use** `device.device_type` → Use `device.platform.slug`
- **Don't hardcode** connection params → Use `ToolkitSettings` methods
- **Don't skip** platform normalization → Always `ToolkitSettings.normalize_platform()`
- **Don't use** plain Django forms → Inherit from `NetBoxModelForm` or `BootstrapForm`
- **Don't forget** pepper requirement → Plugin startup fails without it
- **Don't use** `{{ }}` in commands → Use `< >` for variables
- **Don't create** custom CSS → Use Tabler classes
- **Don't bypass** `ObjectPermission` → Use NetBox's permission system
- **Don't store** plaintext credentials → Use `DeviceCredentialSet` with encryption
- **Don't forget** migrations dependency → Always depend on relevant NetBox migrations

## Quick Reference

**Generate Migration**: `cd /opt/netbox/netbox && python manage.py makemigrations netbox_toolkit_plugin`
**Apply Migrations**: `python manage.py migrate netbox_toolkit_plugin`
**Run Tests**: Use VS Code task "Run Plugin Tests" or `pytest -v`
**Format Code**: Use VS Code task "Ruff: Format & Fix All" or `ruff format . && ruff check --fix .`
**Check Status**: Use VS Code task "Check NetBox Process Status"

## Documentation Structure

- `docs/user/`: End-user guides (installation, configuration, credentials)
- `docs/api/`: REST API documentation (authentication, endpoints, workflows)
- `docs/development/`: Developer guides (setup, architecture, contribution workflow)
- `docs/platform-support.md`: Detailed platform compatibility matrix

