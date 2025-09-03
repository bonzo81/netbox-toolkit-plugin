from django.db import models

from netbox.models import NetBoxModel


class Command(NetBoxModel):
    name = models.CharField(max_length=100)
    command = models.TextField()
    description = models.TextField(blank=True)

    # Platform-based association (required)
    platform = models.ForeignKey(
        to="dcim.Platform",
        on_delete=models.CASCADE,
        related_name="toolkit_commands",
        help_text="Platform this command is designed for (e.g., cisco_ios, cisco_nxos, generic)",
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
        ordering = ["platform", "name"]
        unique_together = [["platform", "name"]]

    def __str__(self):
        return f"{self.name} ({self.platform})"

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
