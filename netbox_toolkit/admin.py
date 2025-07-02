from django.contrib import admin
from netbox.admin import NetBoxModelAdmin
from .models import Command, CommandLog

@admin.register(Command)
class CommandAdmin(NetBoxModelAdmin):
    list_display = ('name', 'platform', 'command_type', 'description')
    list_filter = ('platform', 'command_type')
    search_fields = ('name', 'command', 'description')

@admin.register(CommandLog)
class CommandLogAdmin(NetBoxModelAdmin):
    list_display = ('command', 'device', 'username', 'execution_time')
    list_filter = ('command', 'device', 'username', 'execution_time')
    search_fields = ('command__name', 'device__name', 'username', 'output')
    readonly_fields = ('output', 'execution_time')
