# Generated migration to remove Django custom permissions for object-based permissions migration

from django.db import migrations


def remove_django_permissions(apps, schema_editor):
    """Remove old Django permissions that are no longer needed"""
    Permission = apps.get_model('auth', 'Permission')
    ContentType = apps.get_model('contenttypes', 'ContentType')
    
    try:
        # Get the Command content type
        command_ct = ContentType.objects.get(app_label='netbox_toolkit', model='command')
        
        # Remove the custom Django permissions
        custom_permissions = [
            'execute_show_command',
            'execute_config_command'
        ]
        
        deleted_count = 0
        for codename in custom_permissions:
            count, _ = Permission.objects.filter(
                content_type=command_ct,
                codename=codename
            ).delete()
            deleted_count += count
        
        print(f"Removed {deleted_count} old Django permissions")
        
    except ContentType.DoesNotExist:
        # Command model doesn't exist yet, skip
        print("Command model not found, skipping permission removal")
    except Exception as e:
        print(f"Warning: Could not remove old permissions: {e}")

def restore_django_permissions(apps, schema_editor):
    """Restore Django permissions if migration is reversed"""
    Permission = apps.get_model('auth', 'Permission')
    ContentType = apps.get_model('contenttypes', 'ContentType')
    
    try:
        # Get the Command content type
        command_ct = ContentType.objects.get(app_label='netbox_toolkit', model='command')
        
        # Recreate the custom Django permissions
        permissions_to_create = [
            ('execute_show_command', 'Can execute show commands'),
            ('execute_config_command', 'Can execute configuration commands'),
        ]
        
        for codename, name in permissions_to_create:
            Permission.objects.get_or_create(
                content_type=command_ct,
                codename=codename,
                defaults={'name': name}
            )
        
        print("Restored old Django permissions")
        
    except ContentType.DoesNotExist:
        # Command model doesn't exist, skip
        print("Command model not found, skipping permission restoration")


class Migration(migrations.Migration):
    
    dependencies = [
        ('netbox_toolkit', '0003_permission_system_update'),
    ]

    operations = [
        migrations.RunPython(
            remove_django_permissions,
            restore_django_permissions,
        ),
    ]
