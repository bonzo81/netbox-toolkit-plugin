from django.db import models

from netbox.models import NetBoxModel


class Command(NetBoxModel):
    name = models.CharField(max_length=100)
    command = models.TextField()
    description = models.TextField(blank=True)

    # Platform-based association (supports multiple platforms)
    platforms = models.ManyToManyField(
        to="dcim.Platform",
        related_name="toolkit_commands",
        help_text="Platforms this command is designed for (e.g., cisco_ios, cisco_nxos, generic)",
    )

    # Command categorization
    command_type = models.CharField(
        max_length=50,
        choices=[
            ("show", "Show Command"),
            ("config", "Configuration Command"),
        ],
        default="show",
        help_text="Type of command for categorization and permission control",
    )

    class Meta:
        ordering = ["name"]

    def __str__(self):
        try:
            # Safely get platform names, avoiding recursion during deletion
            if hasattr(self, "_state") and self._state.adding:
                # Object is being created, platforms not yet available
                return self.name

            platform_names = []
            try:
                platforms = self.platforms.all()[:3]
                platform_names = [str(p) for p in platforms]

                if self.platforms.count() > 3:
                    platform_names.append(f"+{self.platforms.count() - 3} more")
            except Exception:
                # If there's any issue accessing platforms, just return the name
                return self.name

            if platform_names:
                return f"{self.name} ({', '.join(platform_names)})"
            else:
                return f"{self.name}"
        except Exception:
            # Fallback to just the name if anything goes wrong
            return getattr(self, "name", "Command")

    def get_absolute_url(self):
        """Return the URL for this object"""
        from django.urls import reverse

        return reverse(
            "plugins:netbox_toolkit_plugin:command_detail", kwargs={"pk": self.pk}
        )


class CommandLog(NetBoxModel):
    command = models.ForeignKey(
        to=Command, on_delete=models.CASCADE, related_name="logs"
    )
    device = models.ForeignKey(
        to="dcim.Device", on_delete=models.CASCADE, related_name="command_logs"
    )
    output = models.TextField()
    username = models.CharField(max_length=100)
    execution_time = models.DateTimeField(auto_now_add=True)

    # Execution details
    success = models.BooleanField(default=True)
    error_message = models.TextField(blank=True)
    execution_duration = models.FloatField(
        blank=True, null=True, help_text="Command execution time in seconds"
    )

    def __str__(self):
        return f"{self.command} on {self.device}"

    def get_absolute_url(self):
        """Return the URL for this object"""
        from django.urls import reverse

        return reverse(
            "plugins:netbox_toolkit_plugin:commandlog_view", kwargs={"pk": self.pk}
        )
