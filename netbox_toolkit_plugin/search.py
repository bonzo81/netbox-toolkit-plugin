from netbox.search import SearchIndex
from .models import Command, CommandLog

class CommandIndex(SearchIndex):
    model = Command
    fields = (
        ('name', 100),
        ('command', 200),
        ('description', 500),
    )
    display_attrs = ('platform', 'command_type', 'description')

class CommandLogIndex(SearchIndex):
    model = CommandLog
    fields = (
        ('command__name', 100),
        ('device__name', 150),
        ('username', 200),
        ('output', 1000),
    )
    display_attrs = ('command', 'device', 'success', 'execution_time')
