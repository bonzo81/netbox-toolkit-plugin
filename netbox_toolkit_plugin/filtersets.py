from django.db.models import Q

from dcim.models import Device, Platform
from netbox.filtersets import NetBoxModelFilterSet

import django_filters

from .models import Command, CommandLog, DeviceCredentialSet


class CommandFilterSet(NetBoxModelFilterSet):
    """Enhanced filtering for commands"""

    platforms = django_filters.ModelMultipleChoiceFilter(
        queryset=Platform.objects.all(),
        label="Platforms",
    )
    platform_slug = django_filters.CharFilter(
        field_name="platforms__slug", lookup_expr="icontains", label="Platform slug"
    )
    command_type = django_filters.ChoiceFilter(
        choices=[("show", "Show Command"), ("config", "Configuration Command")]
    )
    created_after = django_filters.DateTimeFilter(
        field_name="created", lookup_expr="gte"
    )
    created_before = django_filters.DateTimeFilter(
        field_name="created", lookup_expr="lte"
    )
    name_icontains = django_filters.CharFilter(
        field_name="name", lookup_expr="icontains", label="Name contains"
    )
    description_icontains = django_filters.CharFilter(
        field_name="description", lookup_expr="icontains", label="Description contains"
    )

    class Meta:
        model = Command
        fields = ("name", "platforms", "command_type", "description")

    def search(self, queryset, name, value):
        """
        Search across name, command, and description fields
        """
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(name__icontains=value)
            | Q(command__icontains=value)
            | Q(description__icontains=value)
        )


class CommandLogFilterSet(NetBoxModelFilterSet):
    """Enhanced filtering for command logs"""

    device_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Device.objects.all(), label="Device (ID)"
    )
    command_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Command.objects.all(), label="Command (ID)"
    )
    execution_time_after = django_filters.DateTimeFilter(
        field_name="execution_time", lookup_expr="gte"
    )
    execution_time_before = django_filters.DateTimeFilter(
        field_name="execution_time", lookup_expr="lte"
    )
    username_icontains = django_filters.CharFilter(
        field_name="username", lookup_expr="icontains", label="Username contains"
    )
    device_name_icontains = django_filters.CharFilter(
        field_name="device__name", lookup_expr="icontains", label="Device name contains"
    )
    command_name_icontains = django_filters.CharFilter(
        field_name="command__name",
        lookup_expr="icontains",
        label="Command name contains",
    )

    class Meta:
        model = CommandLog
        fields = ("command", "device", "username", "success")

    def search(self, queryset, name, value):
        """
        Search across command name, device name, username
        """
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(command__name__icontains=value)
            | Q(device__name__icontains=value)
            | Q(username__icontains=value)
        )


class DeviceCredentialSetFilterSet(NetBoxModelFilterSet):
    """Filtering for device credential sets"""

    name_icontains = django_filters.CharFilter(
        field_name="name", lookup_expr="icontains", label="Name contains"
    )

    platform_slug = django_filters.CharFilter(
        field_name="platforms__slug", lookup_expr="icontains", label="Platform slug"
    )

    platforms = django_filters.ModelMultipleChoiceFilter(
        queryset=Platform.objects.all(),
        label="Platforms",
    )

    is_active = django_filters.BooleanFilter(label="Active")

    created_after = django_filters.DateTimeFilter(
        field_name="created_at", lookup_expr="gte", label="Created after"
    )

    created_before = django_filters.DateTimeFilter(
        field_name="created_at", lookup_expr="lte", label="Created before"
    )

    last_used_after = django_filters.DateTimeFilter(
        field_name="last_used", lookup_expr="gte", label="Last used after"
    )

    class Meta:
        model = DeviceCredentialSet
        fields = ("name", "platforms", "is_active")

    def search(self, queryset, name, value):
        """
        Search across name, description, owner username, and platform slug fields
        """
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(name__icontains=value)
            | Q(description__icontains=value)
            | Q(owner__username__icontains=value)
            | Q(platforms__slug__icontains=value)
        )
