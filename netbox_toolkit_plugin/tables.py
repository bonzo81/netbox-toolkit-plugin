from netbox.tables import NetBoxTable

import django_tables2 as tables

from .models import Command, CommandLog, DeviceCredentialSet


class CommandTable(NetBoxTable):
    pk = tables.Column(linkify=True, verbose_name="ID")
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
        fields = ("pk", "name", "platforms", "command_type", "description")
        default_columns = ("pk", "name", "platforms", "command_type", "description")
        exclude = ("id",)


class CommandLogTable(NetBoxTable):
    pk = tables.Column(
        linkify=("plugins:netbox_toolkit_plugin:commandlog_view", [tables.A("pk")]),
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

    class Meta(NetBoxTable.Meta):
        model = CommandLog
        fields = (
            "pk",
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
        exclude = ("id",)


class DeviceCredentialSetTable(NetBoxTable):
    """Table for displaying device credential sets"""

    pk = tables.Column(linkify=True, verbose_name="ID")
    name = tables.Column(
        linkify=(
            "plugins:netbox_toolkit_plugin:devicecredentialset_detail",
            [tables.A("pk")],
        )
    )
    platforms = tables.TemplateColumn(
        template_code="""
        {% if record.platforms.exists %}
            {% for platform in record.platforms.all %}
                <a href="{{ platform.get_absolute_url }}">{{ platform }}</a>{% if not forloop.last %}, {% endif %}
            {% endfor %}
        {% else %}
            <em>All platforms</em>
        {% endif %}
        """,
        verbose_name="Platforms",
        orderable=False,
    )
    access_token = tables.TemplateColumn(
        template_code="""
        <div class="d-flex align-items-center">
            <code class="me-2">{{ record.access_token|truncatechars:20 }}...</code>
            <small class="text-muted">View details to reveal full token</small>
        </div>
        """,
        verbose_name="Credential Token",
        orderable=False,
    )
    created_at = tables.DateTimeColumn(verbose_name="Created", format="Y-m-d H:i")
    last_used = tables.DateTimeColumn(
        verbose_name="Last Used", format="Y-m-d H:i", default="Never"
    )
    is_active = tables.BooleanColumn(
        verbose_name="Active", yesno=("Active", "Inactive")
    )

    class Meta(NetBoxTable.Meta):
        model = DeviceCredentialSet
        fields = (
            "pk",
            "name",
            "description",
            "platforms",
            "access_token",
            "is_active",
            "created_at",
            "last_used",
        )
        default_columns = (
            "pk",
            "name",
            "platforms",
            "access_token",
            "is_active",
            "created_at",
            "last_used",
        )
        exclude = ("id",)
