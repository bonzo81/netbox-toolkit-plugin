# Generated migration for Argon2id token support

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('netbox_toolkit_plugin', '0012_alter_command_unique_together_devicecredentialset'),
    ]

    operations = [
        migrations.AlterField(
            model_name='devicecredentialset',
            name='access_token',
            field=models.CharField(
                editable=False,
                help_text='Secure token hash for credential access via API',
                max_length=255,
                unique=True
            ),
        ),
    ]