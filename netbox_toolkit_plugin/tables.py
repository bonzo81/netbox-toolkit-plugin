import logging

from netbox.tables import NetBoxTable

import django_tables2 as tables

from .models import Command, CommandLog, DeviceCredentialSet

# Set up logging for debugging table configuration issues
logger = logging.getLogger(__name__)


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
        fields = ("pk", "name", "platforms", "command_type", "description")
        default_columns = ("pk", "name", "platforms", "command_type", "description")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        logger.debug(
            f"CommandTable initialized. Columns: {[col.name for col in self.columns]}"
        )
        logger.debug(f"CommandTable Meta fields: {self.Meta.fields}")
        logger.debug(
            f"CommandTable Meta exclude: {getattr(self.Meta, 'exclude', 'None')}"
        )
        logger.debug(f"CommandTable Meta default_columns: {self.Meta.default_columns}")


class CommandLogTable(NetBoxTable):
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
        # Remove exclude = ("id",) to allow NetBox's automatic ID column to work with table configuration

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        logger.debug(
            f"CommandLogTable initialized. Columns: {[col.name for col in self.columns]}"
        )
        logger.debug(f"CommandLogTable Meta fields: {self.Meta.fields}")
        logger.debug(
            f"CommandLogTable Meta exclude: {getattr(self.Meta, 'exclude', 'None')}"
        )
        logger.debug(
            f"CommandLogTable Meta default_columns: {self.Meta.default_columns}"
        )


class DeviceCredentialSetTable(NetBoxTable):
    """Table for displaying device credential sets"""

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
            <code class="me-2">{% if record.raw_token %}{{ record.raw_token|truncatechars:20 }}{% else %}{{ record.access_token|truncatechars:20 }}{% endif %}...</code>
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
        # Remove exclude = ("id",) to allow NetBox's automatic ID column to work with table configuration

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        logger.debug(
            f"DeviceCredentialSetTable initialized. Columns: {[col.name for col in self.columns]}"
        )
        logger.debug(f"DeviceCredentialSetTable Meta fields: {self.Meta.fields}")
        logger.debug(
            f"DeviceCredentialSetTable Meta exclude: {getattr(self.Meta, 'exclude', 'None')}"
        )
        logger.debug(
            f"DeviceCredentialSetTable Meta default_columns: {self.Meta.default_columns}"
        )
