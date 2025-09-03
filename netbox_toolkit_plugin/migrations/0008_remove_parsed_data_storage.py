# Generated migration to remove parsed data storage

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('netbox_toolkit_plugin', '0007_alter_commandlog_parsing_template'),
    ]

    operations = [
        # Remove parsed data fields since we now parse fresh from raw output
        migrations.RemoveField(
            model_name='commandlog',
            name='parsed_data',
        ),
        migrations.RemoveField(
            model_name='commandlog',
            name='parsing_success',
        ),
        migrations.RemoveField(
            model_name='commandlog',
            name='parsing_template',
        ),
    ]
