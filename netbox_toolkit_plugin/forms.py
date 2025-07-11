from django import forms
from django.utils.translation import gettext_lazy as _
from netbox.forms import NetBoxModelForm
from utilities.forms.fields import DynamicModelChoiceField
from dcim.models import Platform
from .models import Command, CommandLog

class CommandForm(NetBoxModelForm):
    platform = DynamicModelChoiceField(
        queryset=Platform.objects.all(),
        help_text="Platform this command is designed for (e.g., cisco_ios, cisco_nxos, generic)"
    )
    
    class Meta:
        model = Command
        fields = ('name', 'command', 'description', 'platform', 'command_type', 'tags')

class CommandLogForm(NetBoxModelForm):
    class Meta:
        model = CommandLog
        fields = ('command', 'device', 'output', 'username')

class CommandExecutionForm(forms.Form):
    username = forms.CharField(
        max_length=100,
        help_text="Username for device authentication"
    )
    password = forms.CharField(
        widget=forms.PasswordInput,
        help_text="Password for device authentication"
    )