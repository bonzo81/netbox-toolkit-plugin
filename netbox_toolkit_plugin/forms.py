from django import forms
from django.forms import inlineformset_factory

from dcim.models import Platform
from netbox.forms import NetBoxModelForm
from utilities.forms.fields import DynamicModelMultipleChoiceField

from .models import Command, CommandLog, CommandVariable


class CommandForm(NetBoxModelForm):
    platforms = DynamicModelMultipleChoiceField(
        queryset=Platform.objects.all(),
        help_text="Platforms this command is designed for (e.g., cisco_ios, cisco_nxos, generic)",
        required=True,
    )

    class Meta:
        model = Command
        fields = ("name", "command", "description", "platforms", "command_type", "tags")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Add helpful information about variables to the command field
        self.fields["command"].help_text = (
            "Enter the command to execute on network devices. "
            "Use angle brackets &lt;&gt; to define variables. "
            "Example: 'show interface &lt;interface_name&gt;' or 'show access-list &lt;access_list_name&gt;'"
        )

        # Add JavaScript for auto-detection
        self.fields["command"].widget.attrs.update({"data-variable-detection": "true"})

        # Initialize formset if this is a POST request with data
        if self.is_bound and self.data:
            self.variable_formset = CommandVariableFormSet(
                instance=self.instance, data=self.data, prefix="variables"
            )
        elif self.instance and self.instance.pk:
            self.variable_formset = CommandVariableFormSet(
                instance=self.instance, prefix="variables"
            )
        else:
            self.variable_formset = CommandVariableFormSet(
                instance=self.instance, prefix="variables"
            )

    def is_valid(self):
        # Validate the main form
        form_is_valid = super().is_valid()

        # Validate the formset
        formset_is_valid = self.variable_formset.is_valid()

        return form_is_valid and formset_is_valid

    def clean_command(self):
        """Validate command and auto-detect missing variables."""
        from .utils.variable_parser import CommandVariableParser

        command_text = self.cleaned_data.get("command", "")

        if self.instance and self.instance.pk:
            # For existing commands, validate variables consistency
            is_valid, missing_vars = CommandVariableParser.validate_variables(
                self.instance
            )
            if not is_valid:
                raise forms.ValidationError(
                    f"Command text references undefined variables: {', '.join(missing_vars)}. "
                    "Please define these variables in the Variables section below."
                )

        return command_text

    def save(self, commit=True):
        # Save the main form instance
        instance = super().save(commit=commit)

        # Save the formset
        if commit:
            self.variable_formset.save()

        return instance


class CommandLogForm(NetBoxModelForm):
    class Meta:
        model = CommandLog
        fields = ("command", "device", "output", "username")


# CommandVariable FormSet for managing variables in command creation
CommandVariableFormSet = inlineformset_factory(
    Command,
    CommandVariable,
    fields=[
        "name",
        "display_name",
        "variable_type",
        "required",
        "help_text",
        "default_value",
    ],
    extra=0,
    can_delete=True,
    widgets={
        "variable_type": forms.Select(choices=CommandVariable.VARIABLE_TYPES),
        "help_text": forms.Textarea(attrs={"rows": 2}),
    },
)


class CommandExecutionForm(forms.Form):
    username = forms.CharField(
        max_length=100, help_text="Username for device authentication"
    )
    password = forms.CharField(
        widget=forms.PasswordInput, help_text="Password for device authentication"
    )

    def __init__(self, *args, command=None, device=None, **kwargs):
        super().__init__(*args, **kwargs)

        if command and command.variables.exists():
            for variable in command.variables.all():
                field_name = f"var_{variable.name}"

                if variable.variable_type == "text":
                    self.fields[field_name] = forms.CharField(
                        label=variable.display_name,
                        required=variable.required,
                        help_text=variable.help_text,
                        initial=variable.default_value,
                        widget=forms.TextInput(
                            attrs={
                                "class": "form-control",
                                "placeholder": variable.help_text
                                or f"Enter {variable.display_name.lower()}",
                            }
                        ),
                    )
                elif variable.variable_type == "netbox_interface" and device:
                    choices = [("", f"Select {variable.display_name.lower()}...")]
                    choices.extend([
                        (interface.name, str(interface))
                        for interface in device.interfaces.all()
                    ])

                    self.fields[field_name] = forms.ChoiceField(
                        label=variable.display_name,
                        choices=choices,
                        required=variable.required,
                        help_text=variable.help_text,
                        widget=forms.Select(
                            attrs={
                                "class": "form-select",
                                "data-tomselect": "true",  # For JavaScript enhancement
                            }
                        ),
                    )
                elif variable.variable_type == "netbox_vlan" and device:
                    choices = [("", f"Select {variable.display_name.lower()}...")]
                    # Note: This would need to be implemented based on your VLAN model structure
                    # For now, using a placeholder implementation
                    choices.extend([
                        (vlan.name, str(vlan))
                        for vlan in device.vlans.all()
                        if hasattr(device, "vlans")
                    ])

                    self.fields[field_name] = forms.ChoiceField(
                        label=variable.display_name,
                        choices=choices,
                        required=variable.required,
                        help_text=variable.help_text,
                        widget=forms.Select(
                            attrs={"class": "form-select", "data-tomselect": "true"}
                        ),
                    )
                elif variable.variable_type == "netbox_ip" and device:
                    choices = [("", f"Select {variable.display_name.lower()}...")]
                    # Note: This would need to be implemented based on your IP address model structure
                    # For now, using a placeholder implementation
                    choices.extend([
                        (ip.address, str(ip))
                        for ip in device.ip_addresses.all()
                        if hasattr(device, "ip_addresses")
                    ])

                    self.fields[field_name] = forms.ChoiceField(
                        label=variable.display_name,
                        choices=choices,
                        required=variable.required,
                        help_text=variable.help_text,
                        widget=forms.Select(
                            attrs={"class": "form-select", "data-tomselect": "true"}
                        ),
                    )
