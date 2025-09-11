from django.contrib import admin

from netbox.admin import NetBoxModelAdmin

from .models import Command, CommandLog


@admin.register(Command)
class CommandAdmin(NetBoxModelAdmin):
    list_display = ("name", "get_platforms_display", "command_type", "description")
    list_filter = ("platforms", "command_type")
    search_fields = ("name", "command", "description")
    filter_horizontal = ("platforms",)

    def get_platforms_display(self, obj):
        """Display multiple platforms in admin list view."""
        try:
            platforms = list(obj.platforms.all()[:3])
            platform_names = [str(platform) for platform in platforms]
            if obj.platforms.count() > 3:
                platform_names.append(f"+{obj.platforms.count() - 3} more")
            return ", ".join(platform_names) if platform_names else "No platforms"
        except Exception:
            return "Error loading platforms"

    get_platforms_display.short_description = "Platforms"


@admin.register(CommandLog)
class CommandLogAdmin(NetBoxModelAdmin):
    list_display = ("command", "device", "username", "execution_time")
    list_filter = ("command", "device", "username", "execution_time")
    search_fields = ("command__name", "device__name", "username", "output")
    readonly_fields = ("output", "execution_time")
