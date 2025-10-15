"""Device-related views for the NetBox Toolkit Plugin."""

from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.views import View

from dcim.models import Device
from netbox.views.generic import ObjectView
from utilities.views import ViewTab, register_model_view

from ..forms import VARIABLE_FIELD_PREFIX, CommandExecutionForm
from ..models import Command, DeviceCredentialSet
from ..services.command_service import CommandExecutionService
from ..services.device_service import DeviceService
from ..services.rate_limiting_service import RateLimitingService


@register_model_view(Device, name="toolkit", path="toolkit")
class DeviceToolkitView(ObjectView):
    queryset = Device.objects.all()
    template_name = "netbox_toolkit_plugin/device_toolkit.html"
    base_template = "dcim/device.html"

    # Define tab without a badge counter
    tab = ViewTab(label="Toolkit")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.command_service = CommandExecutionService()
        self.device_service = DeviceService()
        self.rate_limiting_service = RateLimitingService()

    def get_object(self, **kwargs):
        """Get device object with proper 404 error handling"""
        pk = self.kwargs.get("pk") or kwargs.get("pk")
        return get_object_or_404(Device, pk=pk)

    def get(self, request, pk):
        """Return the device toolkit page"""
        self.kwargs = {"pk": pk}  # Set kwargs for get_object
        device = self.get_object()

        # Validate device is ready for commands
        is_valid, error_message, validation_checks = (
            self.device_service.validate_device_for_commands(device)
        )
        if not is_valid:
            messages.warning(request, f"Device validation warning: {error_message}")

        # Get connection info for the device
        connection_info = self.device_service.get_device_connection_info(device)

        # Get available commands for the device with permission filtering
        commands = self._get_filtered_commands(request.user, device)

        # Get rate limit status for UI display
        rate_limit_status = self.rate_limiting_service.get_rate_limit_status(
            device, request.user
        )

        # Initialize empty form - will be populated when command is selected
        form = CommandExecutionForm()
        execution_form = None

        # No credential storage - credentials required for each command execution

        return render(
            request,
            self.template_name,
            {
                "object": device,
                "tab": self.tab,
                "commands": commands,
                "form": form,
                "execution_form": execution_form,
                "device_valid": is_valid,
                "validation_message": error_message,
                "validation_checks": validation_checks,
                "connection_info": connection_info,
                "rate_limit_status": rate_limit_status,
            },
        )

    def _user_has_action_permission(self, user, obj, action):
        """Check if user has permission for a specific action on an object using NetBox's ObjectPermission system"""
        from django.contrib.contenttypes.models import ContentType

        from users.models import ObjectPermission

        # Get content type for the object
        content_type = ContentType.objects.get_for_model(obj)

        # Check if user has any ObjectPermissions with the required action
        user_permissions = ObjectPermission.objects.filter(
            object_types__in=[content_type], actions__contains=[action], enabled=True
        )

        # Check if user is assigned to any groups with this permission
        user_groups = user.groups.all()
        for permission in user_permissions:
            # Check if permission applies to user or user's groups
            if (
                permission.users.filter(id=user.id).exists()
                or permission.groups.filter(
                    id__in=user_groups.values_list("id", flat=True)
                ).exists()
            ):
                # If there are constraints, evaluate them
                if permission.constraints:
                    # Create a queryset with the constraints and check if the object matches
                    queryset = content_type.model_class().objects.filter(
                        **permission.constraints
                    )
                    if queryset.filter(id=obj.id).exists():
                        return True
                else:
                    # No constraints means permission applies to all objects of this type
                    return True

        return False

    def _get_filtered_commands(self, user, device):
        """Get commands for a device filtered by user permissions"""
        # Get all available commands for the device
        all_commands = self.device_service.get_available_commands(device)

        # Filter commands based on user permissions for custom actions
        commands = []
        for command in all_commands:
            # Check if user has permission for the specific action on this command
            if command.command_type == "show":
                # Check for 'execute_show' action permission
                if self._user_has_action_permission(user, command, "execute_show"):
                    commands.append(command)
            elif command.command_type == "config" and self._user_has_action_permission(
                user, command, "execute_config"
            ):
                # Check for 'execute_config' action permission
                commands.append(command)

        return commands

    def _order_parsed_data(self, parsed_data):
        """
        Return parsed data preserving original TextFSM template field order.

        For live parsing results, we preserve the original order from TextFSM
        since it represents the logical field sequence defined in the template.
        """
        # For live parsing, the original order from TextFSM should be preserved
        # No reordering needed as the data comes directly from TextFSM parsing
        return parsed_data

    def _get_base_context(self, request, device):
        """Get base context data for the template"""
        # Validate device is ready for commands
        is_valid, error_message, validation_checks = (
            self.device_service.validate_device_for_commands(device)
        )

        # Get connection info for the device
        connection_info = self.device_service.get_device_connection_info(device)

        # Get available commands for the device with permission filtering
        commands = self._get_filtered_commands(request.user, device)

        # Get rate limit status for UI display
        rate_limit_status = self.rate_limiting_service.get_rate_limit_status(
            device, request.user
        )

        # Initialize empty form
        form = CommandExecutionForm()

        return {
            "object": device,
            "tab": self.tab,
            "commands": commands,
            "form": form,
            "execution_form": None,
            "device_valid": is_valid,
            "validation_message": error_message,
            "validation_checks": validation_checks,
            "connection_info": connection_info,
            "rate_limit_status": rate_limit_status,
        }


class DeviceExecutionModalView(ObjectView):
    """
    HTMX view to return complete execution modal for a specific command
    Regular ObjectView with proper queryset definition
    """

    queryset = Device.objects.all()
    template_name = "netbox_toolkit_plugin/htmx/execution_modal.html"

    def get(self, request, pk):
        """Return rendered HTML for the complete execution modal"""
        device = get_object_or_404(Device, pk=pk)

        command_id = request.GET.get("command_id")

        if not command_id:
            return render(
                request,
                self.template_name,
                {
                    "error": "Command ID is required",
                    "device": device,
                },
            )

        try:
            command = Command.objects.get(id=command_id)

            # Initialize services for rate limiting
            from ..services.rate_limiting_service import RateLimitingService

            rate_limiting_service = RateLimitingService()

            # Create the execution form with the specific command and device
            execution_form = CommandExecutionForm(command=command, device=device)

            # Extract variable fields from the form
            variable_fields = []
            for field_name, field in execution_form.fields.items():
                if field_name.startswith(VARIABLE_FIELD_PREFIX):
                    variable_fields.append({
                        "name": field_name,
                        "field": execution_form[field_name],
                        "label": field.label,
                        "required": field.required,
                        "help_text": field.help_text,
                    })

            # Get rate limit status for UI display
            rate_limit_status = rate_limiting_service.get_rate_limit_status(
                device, request.user
            )

            # Get user's credential sets, filtered by device platform
            # Use the manager method for consistent platform filtering
            user_credential_sets = DeviceCredentialSet.objects.for_user_and_device(
                request.user, device
            )

            return render(
                request,
                self.template_name,
                {
                    "device": device,
                    "command": command,
                    "variable_fields": variable_fields,
                    "has_variables": len(variable_fields) > 0,
                    "rate_limit_status": rate_limit_status,
                    "credential_sets": user_credential_sets,
                },
            )

        except Command.DoesNotExist:
            return render(
                request,
                self.template_name,
                {
                    "error": "Command not found",
                    "device": device,
                },
            )
        except Exception as e:
            return render(
                request,
                self.template_name,
                {
                    "error": str(e),
                    "device": device,
                },
            )


class DeviceRateLimitUpdateView(View):
    """HTMX endpoint for updating rate limiting card content"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.rate_limiting_service = RateLimitingService()

    def get(self, request, pk):
        """Return just the rate limiting card content as HTML"""
        device = get_object_or_404(Device, pk=pk)
        rate_limit_status = self.rate_limiting_service.get_rate_limit_status(
            device, request.user
        )

        return render(
            request,
            "netbox_toolkit_plugin/htmx/rate_limit_card.html",
            {
                "rate_limit_status": rate_limit_status,
            },
        )


class DeviceCommandOutputView(View):
    """HTMX endpoint for updating command output after execution"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.command_service = CommandExecutionService()
        self.rate_limiting_service = RateLimitingService()

    def post(self, request, pk):
        """Execute command and return just the output section"""
        device = get_object_or_404(Device, pk=pk)

        # Get command from form data
        command_id = request.POST.get("command_id")
        credential_set_id = request.POST.get("credential_set_id")
        auth_method = request.POST.get(
            "auth_method", "stored"
        )  # Default to stored for backward compatibility
        username = request.POST.get("username")
        password = request.POST.get("password")

        if not command_id:
            return HttpResponse(
                '<div class="alert alert-danger">Command ID is required</div>',
                status=400,
            )

        # Validate authentication based on method
        if auth_method == "stored":
            if not credential_set_id:
                return HttpResponse(
                    '<div class="alert alert-danger">Credential set is required when using stored credentials</div>',
                    status=400,
                )
        elif auth_method == "onthefly":
            if not username or not password:
                return HttpResponse(
                    '<div class="alert alert-danger">Username and password are required when entering credentials</div>',
                    status=400,
                )
        else:
            return HttpResponse(
                '<div class="alert alert-danger">Invalid authentication method</div>',
                status=400,
            )

        try:
            command = Command.objects.get(id=command_id)

            # Collect variable values from POST data
            variables = {}
            for key, value in request.POST.items():
                if key.startswith(VARIABLE_FIELD_PREFIX):
                    variable_name = key.removeprefix(VARIABLE_FIELD_PREFIX)
                    variables[variable_name] = value

            # Process command text with variable substitution using the parser utility
            from ..utils.variable_parser import CommandVariableParser

            processed_command_text, is_valid, errors = (
                CommandVariableParser.prepare_command_for_execution(command, variables)
            )

            if not is_valid:
                error_messages = "; ".join(errors)
                return HttpResponse(
                    f'<div class="alert alert-danger">{error_messages}</div>',
                    status=400,
                )

            # Create a temporary command object with the processed command text
            # Note: This is an in-memory object used only for execution, not saved to DB
            # Only the fields actually used during execution are set
            temp_command = Command(
                id=command.id,  # For logging reference
                name=command.name,  # For logging and display
                command=processed_command_text,  # The actual command with variables substituted
                command_type=command.command_type,  # For connector selection
                description=command.description,  # For context
            )

            # Execute the command based on authentication method
            if auth_method == "stored":
                # Use existing credential set method
                result = self.command_service.execute_command_with_credential_set(
                    command=temp_command,
                    device=device,
                    credential_set_id=int(credential_set_id),
                    user=request.user,
                    max_retries=1,
                )
            elif auth_method == "onthefly":
                # Use direct username/password method
                result = self.command_service.execute_command_with_retry(
                    command=temp_command,
                    device=device,
                    username=username,
                    password=password,
                    max_retries=1,
                )

            # Render just the command output section
            return render(
                request,
                "netbox_toolkit_plugin/htmx/command_output.html",
                {
                    "command_output": result.output,
                    "execution_success": result.success,
                    "execution_time": getattr(result, "execution_time", None),
                    "executed_command": command,
                    "parsed_data": getattr(result, "parsed_output", None),
                    "parsing_method": getattr(result, "parsing_method", None),
                    "has_syntax_error": getattr(result, "has_syntax_error", False),
                    "syntax_error_type": getattr(result, "syntax_error_type", None),
                    "syntax_error_vendor": getattr(result, "syntax_error_vendor", None),
                    "command_log_id": getattr(result, "command_log_id", None),
                },
            )

        except Command.DoesNotExist:
            return HttpResponse(
                '<div class="alert alert-danger">Command not found</div>', status=404
            )
        except Exception as e:
            return HttpResponse(
                f'<div class="alert alert-danger">Command execution failed: {str(e)}</div>',
                status=500,
            )


class DeviceRecentHistoryView(View):
    """HTMX endpoint for updating recent command history"""

    def get(self, request, pk):
        """Return just the recent history content as HTML"""
        device = get_object_or_404(Device, pk=pk)
        recent_history = device.command_logs.all().order_by("-execution_time")[:3]

        return render(
            request,
            "netbox_toolkit_plugin/htmx/recent_history.html",
            {
                "recent_history": recent_history,
            },
        )
