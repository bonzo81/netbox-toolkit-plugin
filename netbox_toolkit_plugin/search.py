from netbox.search import SearchIndex

from .models import Command, CommandLog, DeviceCredentialSet


class CommandIndex(SearchIndex):
    model = Command
    fields = (
        ("name", 100),
        ("command", 200),
        ("description", 500),
    )
    display_attrs = ("platforms", "command_type", "description")


class CommandLogIndex(SearchIndex):
    model = CommandLog
    fields = (
        ("command__name", 100),
        ("device__name", 150),
        ("username", 200),
        ("output", 1000),
    )
    display_attrs = ("command", "device", "success", "execution_time")


class DeviceCredentialSetIndex(SearchIndex):
    """Search index for DeviceCredentialSet model."""

    model = DeviceCredentialSet
    fields = (
        ("name", 100),
        ("description", 300),
        ("owner__username", 200),
    )
    display_attrs = ("platforms", "is_active", "created_at", "last_used")
