import django_filters
from netbox.filtersets import NetBoxModelFilterSet
from dcim.models import Platform, Device
from .models import Command, CommandLog

class CommandFilterSet(NetBoxModelFilterSet):
    """Enhanced filtering for commands"""
    platform_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Platform.objects.all(),
        label='Platform (ID)',
    )
    platform_slug = django_filters.CharFilter(
        field_name='platform__slug',
        lookup_expr='icontains',
        label='Platform slug'
    )
    command_type = django_filters.ChoiceFilter(
        choices=[('show', 'Show Command'), ('config', 'Configuration Command')]
    )
    created_after = django_filters.DateTimeFilter(
        field_name='created',
        lookup_expr='gte'
    )
    created_before = django_filters.DateTimeFilter(
        field_name='created',
        lookup_expr='lte'
    )
    name_icontains = django_filters.CharFilter(
        field_name='name',
        lookup_expr='icontains',
        label='Name contains'
    )
    description_icontains = django_filters.CharFilter(
        field_name='description',
        lookup_expr='icontains',
        label='Description contains'
    )

    class Meta:
        model = Command
        fields = ('name', 'platform', 'command_type', 'description')

class CommandLogFilterSet(NetBoxModelFilterSet):
    """Enhanced filtering for command logs"""
    device_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Device.objects.all(),
        label='Device (ID)'
    )
    command_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Command.objects.all(),
        label='Command (ID)'
    )
    execution_time_after = django_filters.DateTimeFilter(
        field_name='execution_time',
        lookup_expr='gte'
    )
    execution_time_before = django_filters.DateTimeFilter(
        field_name='execution_time',
        lookup_expr='lte'
    )
    has_parsed_data = django_filters.BooleanFilter(
        field_name='parsed_data',
        lookup_expr='isnull',
        exclude=True,
        label='Has parsed data'
    )
    username_icontains = django_filters.CharFilter(
        field_name='username',
        lookup_expr='icontains',
        label='Username contains'
    )
    device_name_icontains = django_filters.CharFilter(
        field_name='device__name',
        lookup_expr='icontains',
        label='Device name contains'
    )
    command_name_icontains = django_filters.CharFilter(
        field_name='command__name',
        lookup_expr='icontains',
        label='Command name contains'
    )

    class Meta:
        model = CommandLog
        fields = ('command', 'device', 'username', 'success', 'parsing_success')
