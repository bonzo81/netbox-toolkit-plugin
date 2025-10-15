# NetBox Toolkit Plugin - Copilot Instructions

## Unique Tech Stack
- **Scrapli**: Primary network device connection library (SSH/Telnet/NETCONF)
- **Scrapli-Community**: Extended platform support for network devices
- **Netmiko**: SSH client fallback for device connections with legacy device support
- **Tabler**: CSS framework (NetBox uses Tabler, not Bootstrap)
- **Argon2**: Password-based key derivation for credential encryption
- **Comprehensive Settings System**: Platform normalization, security configuration, timeout management

## Response Format
- Don't create test scripts or test cases unless explicitly requested
- Use Context7 tool for retrieving documentation
- Platform names should be normalized using `ToolkitSettings.normalize_platform()`

## Key Architecture Patterns
- Use `device.platform.slug` for connector selection (not device_type)
- Factory pattern with fallback: `ConnectorFactory.create_connector()` with Scrapli→Netmiko fallback
- Service layer: `CommandExecutionService`, `DeviceService`, `CredentialService`, `EncryptionService`, `RateLimitingService`
- NetBox permissions: `ObjectPermission` with `execute_show`/`execute_config` actions
- Platform normalization: `ToolkitSettings.normalize_platform()` - single source of truth

## Plugin-Specific Architecture

### Core Module Structure
```
netbox_toolkit/
├── connectors/         # Device connection abstraction (Scrapli-based with Netmiko fallback)
│   ├── factory.py     # Smart connector selection with platform mapping
│   ├── base.py        # Abstract base connector
│   ├── scrapli_connector.py
│   └── netmiko_connector.py
├── services/          # Business logic layer
│   ├── command_service.py      # Command execution orchestration
│   ├── credential_service.py   # Token-based credential management
│   ├── device_service.py       # Device validation and connection info
│   ├── encryption_service.py   # Argon2-based credential encryption
│   └── rate_limiting_service.py # Execution rate limiting
├── utils/             # Network utilities and error parsing
│   ├── connection.py   # Connection parameter handling
│   ├── error_parser.py # Network error analysis
│   ├── error_sanitizer.py # Sensitive data removal
│   ├── logging.py      # Structured logging
│   ├── netbox_data_validator.py # NetBox data validation
│   ├── network.py      # Network utility functions
│   └── variable_parser.py # Command variable substitution
├── api/               # REST API with command execution endpoints
└── settings.py        # Comprehensive configuration management
```

### Key NetBox Integration Points
- `@register_model_view(Device, name='toolkit', path='toolkit')` - Adds "Toolkit" tab to device pages
- `ViewTab(label='Toolkit')` - Custom device tab integration
- `ObjectPermission` - NetBox's permission system for command execution
- URL namespace: `plugins:netbox_toolkit_plugin:*` for all plugin URLs
- Custom managers: `DeviceCredentialSetManager` with platform filtering

### Enhanced Models & Relationships

#### **Command** (Multi-Platform Support)
- **platforms**: ManyToManyField to NetBox Platform model (not single platform)
- **command_type**: Choice field ("show", "config") for categorization
- **variables**: Related CommandVariable objects for dynamic command parameters
- Commands can target multiple platforms: cisco_ios, cisco_nxos, juniper_junos, etc.

#### **CommandVariable** (NEW - Dynamic Command Parameters)
- **variable_type**: Interface/VLAN/IP selection from NetBox objects or free text
- **required**: Boolean flag for mandatory variables
- **default_value**: Optional default values for variables
- Variable substitution in commands: `show interface {{interface_name}}`

#### **CommandLog** (Enhanced Execution Tracking)
- **execution_duration**: Float field for performance monitoring
- **success**: Boolean field for execution status
- **error_message**: Detailed error information for troubleshooting

#### **DeviceCredentialSet** (Token-Based Authentication)
- **encrypted_username/password**: Argon2-encrypted credentials
- **access_token**: Hash-based API access tokens
- **platforms**: ManyToManyField for credential reuse across platforms
- **owner**: User ownership with NetBox permissions integration

### Advanced Connector Factory Pattern
```python
# Smart connector creation with fallback strategy
connector = ConnectorFactory.create_connector(
    device=device,
    username=credentials["username"],
    password=credentials["password"],
    use_fallback=True  # Enable Scrapli→Netmiko fallback
)

# Platform normalization (single source of truth)
platform = ToolkitSettings.normalize_platform(device.platform.slug)

# Fast-fail logic for immediate Netmiko fallback
result = connector.execute_command(command, credentials)
```

### Comprehensive Service Layer Pattern
- **`CommandExecutionService`**: Command execution orchestration with retry logic and rate limiting
- **`DeviceService`**: Device validation, connection info, and platform compatibility
- **`CredentialService`**: Token-based credential management and validation
- **`EncryptionService`**: Argon2-based credential encryption/decryption
- **`RateLimitingService`**: Execution rate limiting and throttling
- **Syntax error detection**: Enhanced network device response parsing

### Advanced Permission System Integration
```python
def _user_has_action_permission(self, user, obj, action):
    # Uses NetBox's ObjectPermission system
    # Actions: 'execute_show', 'execute_config'
    # Supports platform-based filtering

# Credential set platform filtering
credentials = DeviceCredentialSet.objects.for_user_and_device(user, device)
```

### Enhanced Scrapli Integration Patterns
- **Platform-based connector selection**: Comprehensive platform mapping (cisco_ios, cisco_nxos, etc.)
- **Intelligent fallback strategy**: Fast-fail patterns for immediate Netmiko fallback
- **Socket error handling**: Retry mechanisms with exponential backoff
- **Connection timeout management**: Device-specific timeout configuration
- **Platform normalization**: Single source of truth via `ToolkitSettings.normalize_platform()`

### Comprehensive Settings System
```python
# Platform normalization (single source of truth)
normalized = ToolkitSettings.normalize_platform("ios-xe")  # → "cisco_ios"

# Device-specific timeouts
timeouts = ToolkitSettings.get_timeouts_for_device("WS-C6509-E")  # Catalyst-specific

# Security configuration with pepper requirement
security_config = ToolkitSettings.get_security_config()

# SSH transport options
ssh_options = ToolkitSettings.get_ssh_transport_options()
```

### Platform Support Matrix
| Platform | Primary | Fallback | Notes |
|----------|---------|----------|-------|
| cisco_ios | Scrapli | Netmiko | All IOS variants supported |
| cisco_nxos | Scrapli | Netmiko | NX-OS 9k/7k/5k/3k |
| cisco_iosxr | Scrapli | Netmiko | IOSXR devices |
| juniper_junos | Scrapli | Netmiko | All Junos platforms |
| arista_eos | Scrapli | Netmiko | All EOS versions |
| hp_procurve | Netmiko | - | Direct Netmiko (legacy) |
| paloalto_panos | Netmiko | - | Direct Netmiko (specialized) |

## NetBox Plugin Development Patterns

### Essential NetBox Base Classes
```python
# Models - Choose the right base class:
class NetBoxModel  # Standard model with change logging
class OrganizationalModel  # Adds tenant/tenant group support
class PrimaryModel  # Has primary key field for global uniqueness

# Use NetBoxModel for plugin models:
class Command(NetBoxModel):  # ✅ Correct
    # NetBoxModel provides: change logging, natural keys, etc.
```

### NetBox Model Field Conventions
```python
# Always use these field types for consistency:
name = models.CharField(max_length=100)  # Standard name field
slug = models.SlugField(max_length=100, unique=True)  # URL-friendly identifier
description = models.CharField(max_length=200, blank=True)  # Optional description
comments = models.TextField(blank=True)  # Free-form comments field

# Foreign Keys to NetBox objects:
device = models.ForeignKey('dcim.Device', on_delete=models.CASCADE)
platform = models.ForeignKey('dcim.Platform', on_delete=models.PROTECT)
user = models.ForeignKey('users.User', on_delete=models.CASCADE)

# ManyToMany relationships:
platforms = models.ManyToManyField('dcim.Platform', related_name='toolkit_commands')
```

### NetBox Permission System Integration
```python
# Define permissions in Meta class:
class Meta:
    permissions = [
        ('execute_show', 'Can execute show commands'),
        ('execute_config', 'Can execute configuration commands'),
    ]

# Check permissions in views/services:
from utilities.permissions import get_permission_for_model
from guardian.shortcuts import get_objects_for_user

def _user_has_action_permission(self, user, obj, action):
    permission = get_permission_for_model(obj.__class__, action)
    return user.has_perm(permission)

# Filter objects by user permissions:
commands = get_objects_for_user(user, 'netbox_toolkit_plugin.execute_show', klass=Command)
```

### NetBox View Patterns
```python
# Use NetBox's generic views:
from netbox.views import generic

class CommandView(generic.ObjectView):
    queryset = Command.objects.all()

class CommandListView(generic.ObjectListView):
    queryset = Command.objects.all()
    table = CommandTable

class CommandEditView(generic.ObjectEditView):
    queryset = Command.objects.all()
    form = CommandForm

class CommandDeleteView(generic.ObjectDeleteView):
    queryset = Command.objects.all()

# Register views in urls.py:
urlpatterns = [
    path('commands/', CommandListView.as_view(), name='command_list'),
    path('commands/<int:pk>/', CommandView.as_view(), name='command_detail'),
    path('commands/<int:pk>/edit/', CommandEditView.as_view(), name='command_edit'),
    path('commands/<int:pk>/delete/', CommandDeleteView.as_view(), name='command_delete'),
]
```

### NetBox Form Integration
```python
# Use NetBox's form classes:
from netbox.forms import NetBoxModelForm

class CommandForm(NetBoxModelForm):
    class Meta:
        model = Command
        fields = ['name', 'command', 'description', 'platforms', 'command_type']

# BootstrapForm for non-model forms:
from netbox.forms import BootstrapForm

class CommandExecutionForm(BootstrapForm):
    device = DynamicModelChoiceField(queryset=Device.objects.all())
    command = forms.ModelChoiceField(queryset=Command.objects.all())
```

### NetBox Template Patterns
```html
<!-- Use NetBox's template structure: -->
{% extends 'netbox_toolkit_plugin/base.html' %}
{% load helpers %}

{% block content %}
<div class="row">
    <div class="col-md-8">
        <div class="card">
            <div class="card-header">
                <strong>{% block title %}Command Details{% endblock %}</strong>
            </div>
            <div class="card-body">
                {% block form %}
                {% endblock %}
            </div>
        </div>
    </div>
</div>
{% endblock %}

<!-- Use NetBox's form rendering: -->
{% load form_helpers %}
{{ form|as_table }}

<!-- Use NetBox's object rendering: -->
{% include 'htmx/object_details.html' %}
```

### NetBox API Integration
```python
# Use NetBox's API serializers:
from netbox.api.serializers import NetBoxModelSerializer

class CommandSerializer(NetBoxModelSerializer):
    class Meta:
        model = Command
        fields = ['id', 'name', 'command', 'description', 'platforms', 'command_type']

# Use NetBox's API views:
from netbox.api.views import ModelViewSet

class CommandViewSet(ModelViewSet):
    queryset = Command.objects.all()
    serializer_class = CommandSerializer

# Register API URLs:
router.register('commands', CommandViewSet)
```

### NetBox Migration Patterns
```python
# Always create proper migrations:
from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('netbox_toolkit_plugin', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('dcim', '0150_device_platform'),  # Depend on NetBox migrations
    ]

    operations = [
        migrations.CreateModel(
            name='CommandVariable',
            fields=[
                ('id', models.AutoField(primary_key=True)),
                ('command', models.ForeignKey(
                    on_delete=models.CASCADE,
                    to='netbox_toolkit_plugin.Command'
                )),
            ],
        ),
    ]
```

### NetBox Testing Patterns
```python
# Use NetBox's testing framework:
from netbox.tests import NetBoxTestCase

class CommandTestCase(NetBoxTestCase):
    def setUp(self):
        super().setUp()
        self.platform = Platform.objects.create(name='Cisco IOS', slug='cisco-ios')

    def test_command_creation(self):
        command = Command.objects.create(
            name='Show Version',
            command='show version',
            platforms=[self.platform]
        )
        self.assertEqual(command.name, 'Show Version')

# Use NetBox's test factories:
from dcim.models import Platform

# Test permissions:
def test_user_permissions(self):
    user = User.objects.create_user('testuser')
    permission = Permission.objects.get(codename='execute_show')
    user.user_permissions.add(permission)
```

### NetBox Custom Field and Configuration
```python
# Access plugin configuration:
from django.conf import settings

PLUGIN_CONFIG = settings.PLUGINS_CONFIG.get('netbox_toolkit_plugin', {})

# Use custom fields if needed (in NetBox admin):
# Custom fields should be defined in NetBox admin interface
# Access via: device.cf.custom_field_name

# Use NetBox's settings system:
TIMEOUTS = PLUGIN_CONFIG.get('timeouts', {})
```

### Common Pitfalls to Avoid
- ❌ Don't use device.device_type - use device.platform instead
- ❌ Don't create custom CSS when Tabler classes exist
- ❌ Don't bypass NetBox's permission system or ObjectPermission checks
- ❌ Don't hardcode connection parameters - use ToolkitSettings configuration system
- ❌ Don't forget to handle connection timeouts and retries properly
- ❌ Don't use generic SSH libraries - prefer Scrapli primary with Netmiko fallback
- ❌ Don't skip platform normalization - always use `ToolkitSettings.normalize_platform()`
- ❌ Don't store plaintext credentials - use DeviceCredentialSet with encryption
- ❌ Don't ignore rate limiting - respect execution limits for device protection
- ❌ Don't forget variable substitution in commands with `{{variable_name}}` syntax
- ❌ Don't use plain Django forms - always inherit from NetBox form classes
- ❌ Don't skip NetBox's template structure - extend proper base templates
- ❌ Don't create custom permissions - use NetBox's ObjectPermission system
- ❌ Don't forget to register models in NetBox's plugin system (`__init__.py`)
- ❌ Don't use direct Django model deletion - use NetBox's change logging

