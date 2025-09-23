from django import forms
from django.forms import inlineformset_factory

from dcim.models import Platform
from netbox.forms import NetBoxModelForm
from utilities.forms.fields import DynamicModelMultipleChoiceField

from .models import Command, CommandLog, CommandVariable, DeviceCredentialSet


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


class DeviceCredentialSetForm(NetBoxModelForm):
    """Form for creating/editing device credential sets in GUI only"""

    username = forms.CharField(
        max_length=100,
        help_text="Username for device authentication",
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )

    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
        help_text="Password for device authentication",
    )

    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
        help_text="Confirm password",
        label="Confirm Password",
    )

    platforms = DynamicModelMultipleChoiceField(
        queryset=Platform.objects.all(),
        required=False,
        help_text="Platforms this credential set applies to (leave empty for all platforms)",
    )

    class Meta:
        model = DeviceCredentialSet
        fields = ("name", "description", "platforms", "is_active")
        help_texts = {
            "name": "User-friendly name for this credential set",
            "description": "Optional description of when/where these credentials are used",
            "is_active": "Whether this credential set is active and can be used",
        }

    def __init__(self, *args, **kwargs):
        # Store user for later use in save()
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        # For existing instances, don't require password fields
        if self.instance and self.instance.pk:
            self.fields["password"].required = False
            self.fields["confirm_password"].required = False
            self.fields[
                "password"
            ].help_text += " (leave empty to keep existing password)"
            self.fields[
                "confirm_password"
            ].help_text = "Confirm new password (if changing)"

    def clean_name(self):
        """Validate that the credential set name is unique for this user."""
        name = self.cleaned_data.get("name")
        if not name:
            return name

        # Check for existing credential set with the same name for this user
        if self.user:
            existing_qs = DeviceCredentialSet.objects.filter(owner=self.user, name=name)

            # If editing, exclude the current instance
            if self.instance.pk:
                existing_qs = existing_qs.exclude(pk=self.instance.pk)

            if existing_qs.exists():
                raise forms.ValidationError(
                    f"You already have a credential set named '{name}'. "
                    "Please choose a different name."
                )

        return name

    def clean(self):
        cleaned_data = super().clean()
        if not cleaned_data:
            return cleaned_data

        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        # Password validation for new instances or when password is provided
        if not self.instance.pk or password:  # New instance or password provided
            if not password:
                raise forms.ValidationError(
                    "Password is required for new credential sets"
                )

            if password != confirm_password:
                raise forms.ValidationError("Passwords do not match")

            # Basic password strength validation
            if len(password) < 6:
                raise forms.ValidationError(
                    "Password must be at least 6 characters long"
                )

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)

        # Set owner for new instances
        if not instance.pk and self.user:
            instance.owner = self.user

        if commit:
            # Handle password encryption only if password is provided
            password = self.cleaned_data.get("password")
            if password:  # Only encrypt if password is provided
                from .services.encryption_service import CredentialEncryptionService

                encryption_service = CredentialEncryptionService()
                encrypted_data = encryption_service.encrypt_credentials(
                    self.cleaned_data["username"], password
                )

                instance.encrypted_username = encrypted_data["encrypted_username"]
                instance.encrypted_password = encrypted_data["encrypted_password"]
                instance.encryption_key_id = encrypted_data["key_id"]

                # Generate new access token if this is a new instance or password changed
                if not instance.pk or password:
                    instance.access_token = encryption_service.generate_access_token()

            instance.save()
            self.save_m2m()  # Save many-to-many relationships (platforms)

        return instance
