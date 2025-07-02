from django.shortcuts import render
from django.views.generic import View
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from dcim.models import Device
from .models import Command, CommandLog
from .forms import CommandForm, CommandLogForm, CommandExecutionForm
from netbox.views.generic import ObjectView, ObjectListView, ObjectEditView, ObjectDeleteView, ObjectChangeLogView
from utilities.views import ViewTab, register_model_view
from .services.command_service import CommandExecutionService
from .services.device_service import DeviceService
from .services.rate_limiting_service import RateLimitingService

@register_model_view(Device, name='toolkit', path='toolkit')
class DeviceToolkitView(ObjectView):
    queryset = Device.objects.all()
    template_name = 'netbox_toolkit/device_toolkit.html'
    
    # Define tab without a badge counter
    tab = ViewTab(
        label='Toolkit'
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.command_service = CommandExecutionService()
        self.device_service = DeviceService()
        self.rate_limiting_service = RateLimitingService()

    def get_object(self, **kwargs):
        """Override get_object to properly filter by pk"""
        return Device.objects.get(pk=self.kwargs.get('pk', kwargs.get('pk')))

    def get(self, request, pk):
        self.kwargs = {'pk': pk}  # Set kwargs for get_object
        device = self.get_object()
        
        # Validate device is ready for commands
        is_valid, error_message, validation_checks = self.device_service.validate_device_for_commands(device)
        if not is_valid:
            messages.warning(request, f"Device validation warning: {error_message}")
        
        # Get connection info for the device
        connection_info = self.device_service.get_device_connection_info(device)
        
        # Get available commands for the device with permission filtering
        commands = self._get_filtered_commands(request.user, device)
        
        # Get rate limit status for UI display
        rate_limit_status = self.rate_limiting_service.get_rate_limit_status(device, request.user)
        
        form = CommandExecutionForm()

        # No credential storage - credentials required for each command execution

        return render(request, self.template_name, {
            'object': device,
            'tab': self.tab,
            'commands': commands,
            'form': form,
            'device_valid': is_valid,
            'validation_message': error_message,
            'validation_checks': validation_checks,
            'connection_info': connection_info,
            'rate_limit_status': rate_limit_status,
        })

    def _user_has_action_permission(self, user, obj, action):
        """Check if user has permission for a specific action on an object using NetBox's ObjectPermission system"""
        from django.contrib.contenttypes.models import ContentType
        from users.models import ObjectPermission
        
        # Get content type for the object
        content_type = ContentType.objects.get_for_model(obj)
        
        # Check if user has any ObjectPermissions with the required action
        user_permissions = ObjectPermission.objects.filter(
            object_types__in=[content_type],
            actions__contains=[action],
            enabled=True
        )
        
        # Check if user is assigned to any groups with this permission
        user_groups = user.groups.all()
        for permission in user_permissions:
            # Check if permission applies to user or user's groups
            if (permission.users.filter(id=user.id).exists() or 
                permission.groups.filter(id__in=user_groups.values_list('id', flat=True)).exists()):
                
                # If there are constraints, evaluate them
                if permission.constraints:
                    # Create a queryset with the constraints and check if the object matches
                    queryset = content_type.model_class().objects.filter(**permission.constraints)
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
            if command.command_type == 'show':
                # Check for 'execute_show' action permission
                if self._user_has_action_permission(user, command, 'execute_show'):
                    commands.append(command)
            elif command.command_type == 'config':
                # Check for 'execute_config' action permission  
                if self._user_has_action_permission(user, command, 'execute_config'):
                    commands.append(command)
        
        return commands

    def post(self, request, pk):
        self.kwargs = {'pk': pk}  # Set kwargs for get_object
        device = self.get_object()
        command_id = request.POST.get('command_id')
        
        try:
            command = Command.objects.get(id=command_id)
        except Command.DoesNotExist:
            messages.error(request, "Selected command not found.")
            return self.get(request, pk)
        
        # Check permissions based on command type using NetBox's object-based permissions
        if command.command_type == 'config':
            if not self._user_has_action_permission(request.user, command, 'execute_config'):
                messages.error(request, "You don't have permission to execute configuration commands.")
                return self.get(request, pk)
        elif command.command_type == 'show':
            if not self._user_has_action_permission(request.user, command, 'execute_show'):
                messages.error(request, "You don't have permission to execute show commands.")
                return self.get(request, pk)
        
        # Create a form with the POST data
        form_data = {
            'username': request.POST.get('username', ''),
            'password': request.POST.get('password', '')
        }
        form = CommandExecutionForm(form_data)
        commands = self._get_filtered_commands(request.user, device)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            # Check rate limiting before command execution
            rate_limit_check = self.rate_limiting_service.check_rate_limit(device, request.user)
            
            if not rate_limit_check['allowed']:
                messages.error(request, f"Rate limit exceeded: {rate_limit_check['reason']}")
                
                # Get rate limit status and other context for display
                rate_limit_status = self.rate_limiting_service.get_rate_limit_status(device, request.user)
                is_valid, error_message, validation_checks = self.device_service.validate_device_for_commands(device)
                connection_info = self.device_service.get_device_connection_info(device)
                
                return render(request, self.template_name, {
                    'object': device,
                    'tab': self.tab,
                    'commands': commands,
                    'form': form,
                    'device_valid': is_valid,
                    'validation_message': error_message,
                    'validation_checks': validation_checks,
                    'connection_info': connection_info,
                    'rate_limit_status': rate_limit_status,
                })

            # Execute command using the service with retry for socket error recovery
            result = self.command_service.execute_command_with_retry(
                command, device, username, password, max_retries=1
            )
            
            # No credential storage for security
            
            # Determine overall success and appropriate message
            overall_success = result.success and not result.has_syntax_error
            
            if overall_success:
                messages.success(request, f"Command '{command.name}' executed successfully.")
            elif result.has_syntax_error:
                messages.warning(request, f"Command '{command.name}' executed but syntax error detected: {result.syntax_error_type}")
            else:
                messages.error(request, f"Command execution failed: {result.error_message}")

            # Return a new empty form after execution
            empty_form = CommandExecutionForm()
            
            # Get validation checks and rate limit status for display
            is_valid, error_message, validation_checks = self.device_service.validate_device_for_commands(device)
            connection_info = self.device_service.get_device_connection_info(device)
            rate_limit_status = self.rate_limiting_service.get_rate_limit_status(device, request.user)
            
            return render(request, self.template_name, {
                'object': device,
                'tab': self.tab,
                'commands': commands,
                'form': empty_form,  # Use an empty form for the next command
                'command_output': result.output,
                'executed_command': command,
                'execution_success': overall_success,
                'execution_time': result.execution_time,
                'has_syntax_error': result.has_syntax_error,
                'syntax_error_type': result.syntax_error_type,
                'syntax_error_vendor': result.syntax_error_vendor,
                'parsed_data': result.parsed_output,
                'parsing_success': result.parsing_success,
                'parsing_template': result.parsing_method,
                'device_valid': is_valid,
                'validation_message': error_message,
                'validation_checks': validation_checks,
                'connection_info': connection_info,
                'rate_limit_status': rate_limit_status,
            })
        else:
            messages.error(request, "Please correct the form errors.")
            # Get validation checks and rate limit status for display
            is_valid, error_message, validation_checks = self.device_service.validate_device_for_commands(device)
            connection_info = self.device_service.get_device_connection_info(device)
            rate_limit_status = self.rate_limiting_service.get_rate_limit_status(device, request.user)
            return render(request, self.template_name, {
                'object': device,
                'tab': self.tab,
                'commands': commands,
                'form': form,
                'device_valid': is_valid,
                'validation_message': error_message,
                'validation_checks': validation_checks,
                'connection_info': connection_info,
                'rate_limit_status': rate_limit_status,
            })

# Command views
class CommandListView(ObjectListView):
    queryset = Command.objects.all()
    filterset = None  # Will update this after import
    table = None  # Will update this after import
    template_name = 'netbox_toolkit/command_list.html'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from .filtersets import CommandFilterSet
        from .tables import CommandTable
        self.filterset = CommandFilterSet
        self.table = CommandTable

class CommandEditView(ObjectEditView):
    queryset = Command.objects.all()
    form = CommandForm
    template_name = 'netbox_toolkit/command_edit.html'
    
    def get_success_url(self):
        """Override to use correct plugin namespace"""
        # Try hardcoded URL first to see if the issue is with reverse()
        if self.object and self.object.pk:
            return f'/plugins/toolkit/commands/{self.object.pk}/'
        return '/plugins/toolkit/commands/'
    
    def get_return_url(self, request, instance):
        """Override to use correct plugin namespace for cancel/return links"""
        # Check if there's a return URL in the request
        return_url = request.GET.get('return_url')
        if return_url:
            return return_url
        # Return hardcoded URL
        return '/plugins/toolkit/commands/'
    
    def get_extra_context(self, request, instance):
        """Override to provide additional context with correct URLs"""
        context = super().get_extra_context(request, instance)
        
        # Override any auto-generated URLs that might be using wrong namespace
        context['base_template'] = 'generic/object_edit.html'
        context['return_url'] = self.get_return_url(request, instance)
        
        return context
    
    def form_valid(self, form):
        """Override form_valid to ensure correct URL handling"""
        # Let the parent handle the form saving
        response = super().form_valid(form)
        # The parent should redirect to get_success_url()
        return response

class CommandView(ObjectView):
    queryset = Command.objects.all()
    template_name = 'netbox_toolkit/command.html'
    
    def get_extra_context(self, request, instance):
        """Add permission context to the template"""
        context = super().get_extra_context(request, instance)
        
        # Add permission information for the template using NetBox's object-based permissions
        context['can_execute'] = False
        if instance.command_type == 'show':
            context['can_execute'] = self._user_has_action_permission(request.user, instance, 'execute_show')
        elif instance.command_type == 'config':
            context['can_execute'] = self._user_has_action_permission(request.user, instance, 'execute_config')
        
        # NetBox will automatically handle 'change' and 'delete' permissions through standard actions
        context['can_edit'] = self._user_has_action_permission(request.user, instance, 'change')
        context['can_delete'] = self._user_has_action_permission(request.user, instance, 'delete')
        
        return context

    def _user_has_action_permission(self, user, obj, action):
        """Check if user has permission for a specific action on an object using NetBox's ObjectPermission system"""
        from django.contrib.contenttypes.models import ContentType
        from users.models import ObjectPermission
        
        # Get content type for the object
        content_type = ContentType.objects.get_for_model(obj)
        
        # Check if user has any ObjectPermissions with the required action
        user_permissions = ObjectPermission.objects.filter(
            object_types__in=[content_type],
            actions__contains=[action],
            enabled=True
        )
        
        # Check if user is assigned to any groups with this permission
        user_groups = user.groups.all()
        for permission in user_permissions:
            # Check if permission applies to user or user's groups
            if (permission.users.filter(id=user.id).exists() or 
                permission.groups.filter(id__in=user_groups.values_list('id', flat=True)).exists()):
                
                # If there are constraints, evaluate them
                if permission.constraints:
                    # Create a queryset with the constraints and check if the object matches
                    queryset = content_type.model_class().objects.filter(**permission.constraints)
                    if queryset.filter(id=obj.id).exists():
                        return True
                else:
                    # No constraints means permission applies to all objects of this type
                    return True
        
        return False

class CommandDeleteView(ObjectDeleteView):
    queryset = Command.objects.all()
    
    def get_success_url(self):
        """Override to use correct plugin namespace"""
        from django.urls import reverse
        return reverse('plugins:netbox_toolkit:command_list')

class CommandChangeLogView(ObjectChangeLogView):
    queryset = Command.objects.all()

# CommandLog views
class CommandLogListView(ObjectListView):
    queryset = CommandLog.objects.all()
    filterset = None  # Will update this after import
    table = None  # Will update this after import
    template_name = 'netbox_toolkit/commandlog_list.html'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from .filtersets import CommandLogFilterSet
        from .tables import CommandLogTable
        self.filterset = CommandLogFilterSet
        self.table = CommandLogTable
    
    def get_extra_context(self, request):
        """Override to disable 'Add' button since logs are created automatically"""
        context = super().get_extra_context(request)
        context['add_button_url'] = None  # Disable the add button
        return context

class CommandLogView(ObjectView):
    queryset = CommandLog.objects.all()
    template_name = 'netbox_toolkit/commandlog.html'

class CommandLogChangeLogView(ObjectChangeLogView):
    queryset = CommandLog.objects.all()