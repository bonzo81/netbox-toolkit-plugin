from django.db import migrations


def remove_commandlog_edit_permissions(apps, schema_editor):
    """
    Remove add_commandlog and change_commandlog permissions.
    CommandLog is an immutable audit record - only view and delete are needed.
    """
    Permission = apps.get_model("auth", "Permission")
    ContentType = apps.get_model("contenttypes", "ContentType")

    try:
        # Get the ContentType for CommandLog
        ct = ContentType.objects.get(app_label="netbox_toolkit_plugin", model="commandlog")

        # Delete the add and change permissions
        Permission.objects.filter(
            content_type=ct, codename__in=["add_commandlog", "change_commandlog"]
        ).delete()

        print(f"Removed add_commandlog and change_commandlog permissions")
    except ContentType.DoesNotExist:
        print("ContentType for CommandLog not found - skipping permission cleanup")


def restore_commandlog_edit_permissions(apps, schema_editor):
    """
    Restore add_commandlog and change_commandlog permissions if migration is reversed.
    """
    Permission = apps.get_model("auth", "Permission")
    ContentType = apps.get_model("contenttypes", "ContentType")

    try:
        ct = ContentType.objects.get(app_label="netbox_toolkit_plugin", model="commandlog")

        # Recreate the permissions
        Permission.objects.get_or_create(
            content_type=ct,
            codename="add_commandlog",
            defaults={"name": "Can add command log"},
        )
        Permission.objects.get_or_create(
            content_type=ct,
            codename="change_commandlog",
            defaults={"name": "Can change command log"},
        )

        print(f"Restored add_commandlog and change_commandlog permissions")
    except ContentType.DoesNotExist:
        print("ContentType for CommandLog not found - skipping permission restoration")


class Migration(migrations.Migration):
    dependencies = [
        ("netbox_toolkit_plugin", "0015_alter_command_unique_together_commandlog_notes_and_more"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="commandlog",
            options={
                "default_permissions": ("view", "delete"),
                "ordering": ["-execution_time"],
            },
        ),
        migrations.RunPython(
            remove_commandlog_edit_permissions,
            reverse_code=restore_commandlog_edit_permissions,
        ),
    ]
