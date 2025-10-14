"""
API ViewSet for Command resources
"""

from django.db import transaction

from dcim.models import Device
from netbox.api.viewsets import NetBoxModelViewSet

from drf_spectacular.utils import extend_schema_view
from rest_framework import serializers, status
from rest_framework.decorators import action
from rest_framework.response import Response

from ... import filtersets, models
from ...services.command_service import CommandExecutionService
from ...services.rate_limiting_service import RateLimitingService
from ..mixins import APIResponseMixin, PermissionCheckMixin
from ..schemas import (
    COMMAND_BULK_EXECUTE_SCHEMA,
    COMMAND_CREATE_SCHEMA,
    COMMAND_DESTROY_SCHEMA,
    COMMAND_EXECUTE_SCHEMA,
    COMMAND_LIST_SCHEMA,
    COMMAND_PARTIAL_UPDATE_SCHEMA,
    COMMAND_RETRIEVE_SCHEMA,
    COMMAND_UPDATE_SCHEMA,
)
from ..serializers import (
    BulkCommandExecutionSerializer,
    CommandExecutionSerializer,
    CommandSerializer,
)


@extend_schema_view(
    list=COMMAND_LIST_SCHEMA,
    retrieve=COMMAND_RETRIEVE_SCHEMA,
    create=COMMAND_CREATE_SCHEMA,
    update=COMMAND_UPDATE_SCHEMA,
    partial_update=COMMAND_PARTIAL_UPDATE_SCHEMA,
    destroy=COMMAND_DESTROY_SCHEMA,
)
class CommandViewSet(NetBoxModelViewSet, APIResponseMixin, PermissionCheckMixin):
    queryset = models.Command.objects.all()
    serializer_class = CommandSerializer
    filterset_class = filtersets.CommandFilterSet
    # Using custom RateLimitingService instead of generic API throttling
    # NetBox automatically handles object-based permissions - no need for explicit permission_classes

    def get_queryset(self):
        """NetBox will automatically filter based on user's ObjectPermissions"""
        # NetBox's object-based permission system will automatically filter this queryset
        # based on the user's ObjectPermissions for 'view' action on Command objects
        return super().get_queryset()

    def _get_variable_validation_suggestions(self, variable, device):
        """Get helpful suggestions for variable validation errors"""
        suggestions = []

        if variable.variable_type == "netbox_interface":
            suggestions.append(
                f"Use the variable-choices endpoint to see available interfaces: GET /api/plugins/netbox-toolkit/commands/{variable.command_id}/variable-choices/?device_id={device.id}"
            )
            suggestions.append("Interface names should match exactly (case-sensitive)")
        elif variable.variable_type == "netbox_vlan":
            suggestions.append(
                f"Use the variable-choices endpoint to see available VLANs: GET /api/plugins/netbox-toolkit/commands/{variable.command_id}/variable-choices/?device_id={device.id}"
            )
            suggestions.append("VLAN IDs should be numeric")
        elif variable.variable_type == "netbox_ip":
            suggestions.append(
                f"Use the variable-choices endpoint to see available IP addresses: GET /api/plugins/netbox-toolkit/commands/{variable.command_id}/variable-choices/?device_id={device.id}"
            )
            suggestions.append(
                "IP addresses should be in CIDR notation (e.g., '192.168.1.1/24')"
            )
        else:
            suggestions.append(
                f"Variable type '{variable.variable_type}' - check the variable definition for format requirements"
            )
            if variable.help_text:
                suggestions.append(f"Help text: {variable.help_text}")

        return suggestions

    @COMMAND_EXECUTE_SCHEMA
    @action(detail=True, methods=["post"], url_path="execute")
    def execute_command(self, request, pk=None):
        """Execute a command on a device using credential token"""
        command = self.get_object()

        # Validate input using serializer - use NetBox pattern
        execution_serializer = CommandExecutionSerializer(
            data=request.data, context={"request": request}
        )
        execution_serializer.is_valid(raise_exception=True)

        validated_data = execution_serializer.validated_data
        device = validated_data["device"]
        credential_token = validated_data["credential_token"]
        variables = validated_data.get("variables", {})

        # Process command variables if present
        if command.variables.exists():
            from ...models import Command as CommandModel
            from ...utils.netbox_data_validator import NetBoxDataValidator
            from ...utils.variable_parser import CommandVariableParser

            # First validate NetBox data variables against the device
            for variable in command.variables.all():
                if variable.name in variables:
                    value = variables[variable.name]
                    is_valid, error_msg = NetBoxDataValidator.validate_variable_value(
                        device, variable.variable_type, variable.name, value
                    )
                    if not is_valid:
                        raise serializers.ValidationError({
                            "variables": {
                                variable.name: f"Invalid value '{value}' for variable '{variable.name}': {error_msg}. Please check the variable requirements and try again."
                            },
                            "validation_details": {
                                "variable_name": variable.name,
                                "variable_type": variable.variable_type,
                                "provided_value": value,
                                "error_type": "netbox_data_validation",
                                "suggestions": self._get_variable_validation_suggestions(
                                    variable, device
                                ),
                            },
                        })

            processed_command_text, is_valid, errors = (
                CommandVariableParser.prepare_command_for_execution(command, variables)
            )

            if not is_valid:
                # Enhance error messages with more context and actionable information
                if isinstance(errors, dict):
                    enhanced_errors = {}
                    for var_name, error in errors.items():
                        enhanced_errors[var_name] = (
                            f"Variable '{var_name}' validation failed: {error}. Please check the variable format and requirements."
                        )
                else:
                    # Handle case where errors is a list of strings
                    enhanced_errors = [
                        f"Variable validation failed: {error}. Please check the variable format and requirements."
                        for error in errors
                    ]

                raise serializers.ValidationError({
                    "variables": enhanced_errors,
                    "validation_details": {
                        "error_type": "variable_parsing",
                        "total_errors": len(errors),
                        "suggestions": "Please ensure all required variables are provided and use the correct format. Use the variable-choices endpoint to see available options.",
                    },
                })

            # Create temporary command object with processed text
            temp_command = CommandModel(
                id=command.id,
                name=command.name,
                command=processed_command_text,
                command_type=command.command_type,
                description=command.description,
            )
            temp_command.platforms.set(command.platforms.all())
            command = temp_command

        # Check permissions based on command type using NetBox's object-based permissions
        if command.command_type == "config":
            if not self._user_has_action_permission(
                request.user, command, "execute_config"
            ):
                return Response(
                    {
                        "error": "You do not have permission to execute configuration commands"
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )
        elif command.command_type == "show" and not self._user_has_action_permission(
            request.user, command, "execute_show"
        ):
            return Response(
                {"error": "You do not have permission to execute show commands"},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Check custom rate limiting (device-specific with bypass rules)
        rate_limiting_service = RateLimitingService()
        rate_limit_check = rate_limiting_service.check_rate_limit(device, request.user)

        if not rate_limit_check["allowed"]:
            return Response(
                {
                    "error": "Rate limit exceeded",
                    "details": {
                        "reason": rate_limit_check["reason"],
                        "current_count": rate_limit_check["current_count"],
                        "limit": rate_limit_check["limit"],
                        "time_window_minutes": rate_limit_check["time_window_minutes"],
                    },
                },
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )

        # Execute command using the service with credential token
        command_service = CommandExecutionService()
        result = command_service.execute_command_with_token(
            command, device, credential_token, request.user, max_retries=1
        )

        # Determine overall success - failed if either execution failed or syntax error detected
        overall_success = result.success and not result.has_syntax_error

        # Prepare response data
        response_data = {
            "success": overall_success,
            "output": result.output,
            "error_message": result.error_message,
            "execution_time": result.execution_time,
            "command": {
                "id": command.id,
                "name": command.name,
                "command_type": command.command_type,
            },
            "device": {"id": device.id, "name": device.name},
        }

        # Add syntax error information if detected
        if result.has_syntax_error:
            response_data["syntax_error"] = {
                "detected": True,
                "type": result.syntax_error_type,
                "vendor": result.syntax_error_vendor,
                "guidance_provided": True,
            }
        else:
            response_data["syntax_error"] = {"detected": False}

        # Add parsing information if available
        if result.parsing_success and result.parsed_output:
            response_data["parsed_output"] = {
                "success": True,
                "method": result.parsing_method,
                "data": result.parsed_output,
            }
        else:
            response_data["parsed_output"] = {
                "success": False,
                "method": None,
                "error": result.parsing_error,
            }

        # Return appropriate status code
        status_code = (
            status.HTTP_200_OK if overall_success else status.HTTP_400_BAD_REQUEST
        )

        return Response(response_data, status=status_code)

    @action(detail=True, methods=["get"], url_path="variable-choices")
    def variable_choices(self, request, pk=None):
        """Get available choices for NetBox data variables for a specific device"""
        command = self.get_object()
        device_id = request.query_params.get("device_id")

        if not device_id:
            raise serializers.ValidationError({"device_id": "Device ID is required"})

        try:
            device = Device.objects.get(id=device_id)
        except Device.DoesNotExist as e:
            raise serializers.ValidationError({
                "device_id": f"Device with ID {device_id} not found"
            }) from e

        variable_choices = {}

        for variable in command.variables.all():
            if variable.variable_type == "text":
                # Text variables don't have predefined choices
                variable_choices[variable.name] = {
                    "type": "text",
                    "choices": None,
                    "help_text": variable.help_text,
                    "default_value": variable.default_value,
                }
            elif variable.variable_type == "netbox_interface":
                # Get available interfaces for the device
                interfaces = device.interfaces.all().order_by("name")
                choices = [
                    {
                        "value": interface.name,
                        "display": f"{interface.name} ({interface.type})",
                        "id": interface.id,
                        "enabled": interface.enabled,
                    }
                    for interface in interfaces
                ]
                variable_choices[variable.name] = {
                    "type": "netbox_interface",
                    "choices": choices,
                    "help_text": variable.help_text,
                    "default_value": variable.default_value,
                }
            elif variable.variable_type == "netbox_vlan":
                # Get available VLANs for the device (if device has VLANs)
                if hasattr(device, "vlans"):
                    vlans = device.vlans.all().order_by("vid")
                    choices = [
                        {
                            "value": str(vlan.vid),
                            "display": f"VLAN {vlan.vid} ({vlan.name})",
                            "id": vlan.id,
                            "name": vlan.name,
                        }
                        for vlan in vlans
                    ]
                else:
                    # Fallback to site VLANs if device doesn't have direct VLANs
                    from ipam.models import VLAN

                    vlans = VLAN.objects.filter(site=device.site).order_by("vid")
                    choices = [
                        {
                            "value": str(vlan.vid),
                            "display": f"VLAN {vlan.vid} ({vlan.name})",
                            "id": vlan.id,
                            "name": vlan.name,
                        }
                        for vlan in vlans
                    ]

                variable_choices[variable.name] = {
                    "type": "netbox_vlan",
                    "choices": choices,
                    "help_text": variable.help_text,
                    "default_value": variable.default_value,
                }
            elif variable.variable_type == "netbox_ip":
                # Get IP addresses associated with the device
                ip_addresses = device.ip_addresses.all().order_by("address")
                choices = [
                    {
                        "value": str(ip.address.ip),
                        "display": f"{ip.address} ({ip.status})",
                        "id": ip.id,
                        "status": ip.status,
                    }
                    for ip in ip_addresses
                ]
                variable_choices[variable.name] = {
                    "type": "netbox_ip",
                    "choices": choices,
                    "help_text": variable.help_text,
                    "default_value": variable.default_value,
                }

        return Response({
            "device_id": device_id,
            "device_name": device.name,
            "command_id": command.id,
            "command_name": command.name,
            "variables": variable_choices,
        })

    @COMMAND_BULK_EXECUTE_SCHEMA
    @action(detail=False, methods=["post"], url_path="bulk-execute")
    def bulk_execute(self, request):
        """Execute multiple commands on multiple devices with variable support"""
        executions = request.data.get("executions", [])

        if not executions:
            raise serializers.ValidationError({"executions": "No executions provided"})

        results = []

        with transaction.atomic():
            for i, execution_data in enumerate(executions):
                try:
                    # Validate each execution using serializer
                    execution_serializer = BulkCommandExecutionSerializer(
                        data=execution_data, context={"request": request}
                    )
                    if not execution_serializer.is_valid():
                        results.append({
                            "execution_id": i + 1,
                            "success": False,
                            "error": "Validation failed",
                            "details": execution_serializer.errors,
                        })
                        continue

                    validated_data = execution_serializer.validated_data
                    command_id = validated_data["command_id"]
                    device_id = validated_data["device_id"]
                    credential_token = validated_data["credential_token"]
                    variables = validated_data.get("variables", {})

                    # Get command and device objects
                    try:
                        command = models.Command.objects.get(id=command_id)
                        device = Device.objects.get(id=device_id)
                    except (models.Command.DoesNotExist, Device.DoesNotExist) as e:
                        results.append({
                            "execution_id": i + 1,
                            "success": False,
                            "error": f"Object not found: {str(e)}",
                        })
                        continue

                    # Process variables if present
                    if command.variables.exists() and variables:
                        from ...models import Command as CommandModel
                        from ...utils.variable_parser import CommandVariableParser

                        processed_command_text, is_valid, errors = (
                            CommandVariableParser.prepare_command_for_execution(
                                command, variables
                            )
                        )

                        if not is_valid:
                            results.append({
                                "execution_id": i + 1,
                                "success": False,
                                "error": "Variable validation failed",
                                "details": {"variables": errors},
                            })
                            continue

                        # Create temporary command object with processed text
                        temp_command = CommandModel(
                            id=command.id,
                            name=command.name,
                            command=processed_command_text,
                            command_type=command.command_type,
                            description=command.description,
                        )
                        temp_command.platforms.set(command.platforms.all())
                        command = temp_command

                    # Check permissions
                    action = (
                        "execute_config"
                        if command.command_type == "config"
                        else "execute_show"
                    )
                    if not self._user_has_action_permission(
                        request.user, command, action
                    ):
                        results.append({
                            "execution_id": i + 1,
                            "success": False,
                            "error": "Insufficient permissions",
                        })
                        continue

                    # Execute command using credential token
                    command_service = CommandExecutionService()
                    result = command_service.execute_command_with_token(
                        command, device, credential_token, request.user, max_retries=1
                    )

                    # Note: Command log entry is automatically created by the service

                    results.append({
                        "execution_id": i + 1,
                        "success": result.success and not result.has_syntax_error,
                        "command_log_id": result.command_log_id,
                        "execution_time": result.execution_time,
                    })

                except Exception as e:
                    from ...utils.error_sanitizer import ErrorSanitizer

                    sanitized_error = ErrorSanitizer.sanitize_api_error(
                        e, "execute command"
                    )
                    results.append({
                        "execution_id": i + 1,
                        "success": False,
                        "error": sanitized_error,
                    })

        # Generate summary
        total = len(results)
        successful = sum(1 for r in results if r.get("success", False))
        failed = total - successful

        return Response(
            {
                "results": results,
                "summary": {"total": total, "successful": successful, "failed": failed},
            },
            status=status.HTTP_200_OK,
        )
