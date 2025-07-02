from django.db import models
from django.core.exceptions import ValidationError
from netbox.models import NetBoxModel
from dcim.models import Device

class Command(NetBoxModel):
    name = models.CharField(max_length=100)
    command = models.TextField()
    description = models.TextField(blank=True)
    
    # Platform-based association (required)
    platform = models.ForeignKey(
        to='dcim.Platform',
        on_delete=models.CASCADE,
        related_name='toolkit_commands',
        help_text="Platform this command is designed for (e.g., cisco_ios, cisco_nxos, generic)"
    )
    
    # Command categorization
    command_type = models.CharField(
        max_length=50,
        choices=[
            ('show', 'Show Command'),
            ('config', 'Configuration Command'),
        ],
        default='show',
        help_text="Type of command for categorization and permission control"
    )

    class Meta:
        ordering = ['platform', 'name']
        unique_together = [['platform', 'name']]

    def __str__(self):
        return f"{self.name} ({self.platform})"
    
    def get_absolute_url(self):
        """Return the URL for this object"""
        from django.urls import reverse
        return reverse('plugins:netbox_toolkit:command_detail', kwargs={'pk': self.pk})

class CommandLog(NetBoxModel):
    command = models.ForeignKey(
        to=Command,
        on_delete=models.CASCADE,
        related_name='logs'
    )
    device = models.ForeignKey(
        to='dcim.Device',
        on_delete=models.CASCADE,
        related_name='command_logs'
    )
    output = models.TextField()
    username = models.CharField(max_length=100)
    execution_time = models.DateTimeField(auto_now_add=True)
    
    # Execution details added in migration
    success = models.BooleanField(default=True)
    error_message = models.TextField(blank=True)
    execution_duration = models.FloatField(
        blank=True,
        null=True,
        help_text="Command execution time in seconds"
    )
    
    # Parsing details for TextFSM
    parsed_data = models.JSONField(
        blank=True,
        null=True,
        help_text="Parsed structured data from command output"
    )
    parsing_success = models.BooleanField(
        default=False,
        help_text="Whether the output was successfully parsed"
    )
    parsing_template = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Name of the TextFSM template used for parsing"
    )

    def __str__(self):
        return f"{self.command} on {self.device}"
    
    def get_absolute_url(self):
        """Return the URL for this object"""
        from django.urls import reverse
        return reverse('plugins:netbox_toolkit:commandlog_view', kwargs={'pk': self.pk})