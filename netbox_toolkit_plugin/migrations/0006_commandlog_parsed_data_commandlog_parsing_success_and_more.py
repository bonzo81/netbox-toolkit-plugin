# Generated by Django 5.1.4 on 2025-05-29 11:47

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("netbox_toolkit_plugin", "0005_alter_command_options_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="commandlog",
            name="parsed_data",
            field=models.JSONField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="commandlog",
            name="parsing_success",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="commandlog",
            name="parsing_template",
            field=models.CharField(blank=True, max_length=255),
        ),
    ]
