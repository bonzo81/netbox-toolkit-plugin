from netbox.tables import NetBoxTable

import django_tables2 as tables

from .models import Command, CommandLog


class CommandTable(NetBoxTable):
    name = tables.Column(
        linkify=("plugins:netbox_toolkit_plugin:command_detail", [tables.A("pk")])
    )
    platforms = tables.TemplateColumn(
        template_code="""
        {% for platform in record.platforms.all %}
            <a href="{{ platform.get_absolute_url }}">{{ platform }}</a>{% if not forloop.last %}, {% endif %}
        {% endfor %}
        """,
        verbose_name="Platforms",
        orderable=False,
    )
    command_type = tables.Column()

    class Meta(NetBoxTable.Meta):
        model = Command
        fields = ("pk", "id", "name", "platforms", "command_type", "description")
        default_columns = ("pk", "name", "platforms", "command_type", "description")


class CommandLogTable(NetBoxTable):
    pk = tables.Column(
        linkify=(
            "plugins:netbox_toolkit_plugin:commandlog_view",
            [tables.A("pk")],
        ),
        verbose_name="ID",
    )
    command = tables.Column(
        linkify=(
            "plugins:netbox_toolkit_plugin:command_detail",
            [tables.A("command.pk")],
        )
    )
    device = tables.Column(linkify=True)
    success = tables.BooleanColumn(verbose_name="Status", yesno=("Success", "Failed"))

    # Remove actions column entirely
    actions = False

    class Meta(NetBoxTable.Meta):
        model = CommandLog
        fields = (
            "pk",
            "id",
            "command",
            "device",
            "username",
            "execution_time",
            "success",
            "execution_duration",
        )
        default_columns = (
            "pk",
            "command",
            "device",
            "username",
            "execution_time",
            "success",
        )
