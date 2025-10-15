# Generated manually - Add CommandVariable model for command variables support

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('netbox_toolkit_plugin', '0009_convert_platform_to_many_to_many'),
    ]

    operations = [
        migrations.CreateModel(
            name='CommandVariable',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('name', models.CharField(
                    max_length=100,
                    help_text="Variable name as used in the command (e.g., 'interface_name')"
                )),
                ('display_name', models.CharField(
                    max_length=200,
                    help_text="Human-readable variable name shown to users"
                )),
                ('variable_type', models.CharField(
                    max_length=50,
                    choices=[
                        ('text', 'Free Text'),
                        ('netbox_interface', 'Device Interface'),
                        ('netbox_vlan', 'VLAN'),
                        ('netbox_ip', 'IP Address'),
                    ],
                    default='text',
                    help_text="Type of variable - determines the input method"
                )),
                ('required', models.BooleanField(
                    default=True,
                    help_text="Whether this variable must be provided to execute the command"
                )),
                ('help_text', models.TextField(
                    blank=True,
                    help_text="Additional help text shown to users for this variable"
                )),
                ('default_value', models.CharField(
                    max_length=200,
                    blank=True,
                    help_text="Default value for this variable (optional)"
                )),
                ('command', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='variables',
                    to='netbox_toolkit_plugin.command',
                    help_text="The command this variable belongs to"
                )),
            ],
            options={
                'ordering': ['command', 'name'],
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='commandvariable',
            unique_together={('command', 'name')},
        ),
    ]