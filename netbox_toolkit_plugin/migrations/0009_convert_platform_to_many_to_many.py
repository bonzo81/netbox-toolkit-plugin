# Generated migration to convert platform ForeignKey to ManyToMany relationship

from django.db import migrations, models


def migrate_platform_data(apps, schema_editor):
    """Migrate existing platform foreign key data to many-to-many relationship."""
    Command = apps.get_model('netbox_toolkit_plugin', 'Command')

    for command in Command.objects.all():
        if hasattr(command, 'platform') and command.platform:
            # Add the existing platform to the new platforms field
            command.platforms.add(command.platform)


def reverse_migrate_platform_data(apps, schema_editor):
    """Reverse migration - copy first platform from many-to-many back to foreign key."""
    Command = apps.get_model('netbox_toolkit_plugin', 'Command')

    for command in Command.objects.all():
        first_platform = command.platforms.first()
        if first_platform:
            command.platform = first_platform
            command.save()


class Migration(migrations.Migration):

    dependencies = [
        ('dcim', '0001_initial'),
        ('netbox_toolkit_plugin', '0008_remove_parsed_data_storage'),
    ]

    operations = [
        # Add the new ManyToMany field
        migrations.AddField(
            model_name='command',
            name='platforms',
            field=models.ManyToManyField(
                help_text='Platforms this command is designed for (e.g., cisco_ios, cisco_nxos, generic)',
                related_name='toolkit_commands',
                to='dcim.platform'
            ),
        ),

        # Data migration to copy existing platform data to the new field
        migrations.RunPython(
            code=migrate_platform_data,
            reverse_code=reverse_migrate_platform_data,
        ),

        # Remove the old ForeignKey field
        migrations.RemoveField(
            model_name='command',
            name='platform',
        ),

        # Update Meta options
        migrations.AlterModelOptions(
            name='command',
            options={'ordering': ['name']},
        ),
    ]
