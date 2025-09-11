from django import forms

from dcim.models import Platform
from netbox.forms import NetBoxModelForm
from utilities.forms.fields import DynamicModelMultipleChoiceField

from .models import Command, CommandLog


class CommandForm(NetBoxModelForm):
    platforms = DynamicModelMultipleChoiceField(
        queryset=Platform.objects.all(),
        help_text="Platforms this command is designed for (e.g., cisco_ios, cisco_nxos, generic)",
        required=True,
    )

    class Meta:
        model = Command
        fields = ("name", "command", "description", "platforms", "command_type", "tags")


class CommandLogForm(NetBoxModelForm):
    class Meta:
        model = CommandLog
        fields = ("command", "device", "output", "username")


class CommandExecutionForm(forms.Form):
    username = forms.CharField(
        max_length=100, help_text="Username for device authentication"
    )
    password = forms.CharField(
        widget=forms.PasswordInput, help_text="Password for device authentication"
    )
