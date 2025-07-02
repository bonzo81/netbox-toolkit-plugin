import django_tables2 as tables
from netbox.tables import NetBoxTable, columns
from .models import Command, CommandLog

class CommandTable(NetBoxTable):
    name = tables.Column(
        linkify=('plugins:netbox_toolkit:command_detail', [tables.A('pk')])
    )
    platform = tables.Column(
        linkify=True
    )
    command_type = tables.Column()
    
    class Meta(NetBoxTable.Meta):
        model = Command
        fields = ('pk', 'id', 'name', 'platform', 'command_type', 'description')
        default_columns = ('pk', 'name', 'platform', 'command_type', 'description')

class CommandLogTable(NetBoxTable):
    command = tables.Column(
        linkify=('plugins:netbox_toolkit:command_detail', [tables.A('command.pk')])
    )
    device = tables.Column(
        linkify=True
    )
    success = tables.BooleanColumn(
        verbose_name='Status',
        yesno=('Success', 'Failed')
    )
    
    # Remove actions column entirely
    actions = False
    
    class Meta(NetBoxTable.Meta):
        model = CommandLog
        fields = ('pk', 'id', 'command', 'device', 'username', 'execution_time', 'success', 'execution_duration')
        default_columns = ('pk', 'command', 'device', 'username', 'execution_time', 'success')
