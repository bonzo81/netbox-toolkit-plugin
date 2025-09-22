# Remove orphaned variables column from Command table
# This column was added by a previous migration but removed from the model

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('netbox_toolkit_plugin', '0010_add_command_variables'),
    ]

    operations = [
        migrations.RunSQL(
            "ALTER TABLE netbox_toolkit_plugin_command DROP COLUMN IF EXISTS variables;",
            reverse_sql="-- Cannot reverse this operation safely"
        ),
    ]