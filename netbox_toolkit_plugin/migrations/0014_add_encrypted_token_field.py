# Generated migration for adding encrypted_token field

import django.db.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('netbox_toolkit_plugin', '0013_alter_devicecredentialset_access_token'),
    ]

    operations = [
        migrations.AddField(
            model_name='devicecredentialset',
            name='encrypted_token',
            field=models.TextField(
                blank=True,
                editable=False,
                help_text='Encrypted raw token for display in UI',
            ),
        ),
    ]