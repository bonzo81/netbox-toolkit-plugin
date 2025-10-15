from django.contrib import admin

from netbox.admin import NetBoxModelAdmin

from .models import Command, CommandLog, DeviceCredentialSet


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


@admin.register(DeviceCredentialSet)
class DeviceCredentialSetAdmin(NetBoxModelAdmin):
    """Admin interface for DeviceCredentialSet model."""

    list_display = (
        "name",
        "owner",
        "get_platforms_display",
        "is_active",
        "created_at",
        "last_used",
    )
    list_filter = ("is_active", "created_at", "platforms", "owner")
    search_fields = ("name", "description", "owner__username")
    filter_horizontal = ("platforms",)
    readonly_fields = (
        "encrypted_username",
        "encrypted_password",
        "encryption_key_id",
        "access_token",
        "created_at",
        "last_used",
    )

    fieldsets = (
        (
            "Basic Information",
            {"fields": ("name", "description", "owner", "is_active")},
        ),
        ("Platform Configuration", {"fields": ("platforms",)}),
        (
            "Security Information",
            {
                "fields": (
                    "access_token",
                    "encrypted_username",
                    "encrypted_password",
                    "encryption_key_id",
                ),
                "classes": ("collapse",),
            },
        ),
        ("Metadata", {"fields": ("created_at", "last_used"), "classes": ("collapse",)}),
    )

    def get_platforms_display(self, obj):
        """Display multiple platforms in admin list view."""
        try:
            platforms = list(obj.platforms.all()[:3])
            if not platforms:
                return "All platforms"
            platform_names = [str(platform) for platform in platforms]
            if obj.platforms.count() > 3:
                platform_names.append(f"+{obj.platforms.count() - 3} more")
            return ", ".join(platform_names)
        except Exception:
            return "Error loading platforms"

    get_platforms_display.short_description = "Platforms"

    def get_queryset(self, request):
        """Users can only see their own credential sets in admin."""
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(owner=request.user)
