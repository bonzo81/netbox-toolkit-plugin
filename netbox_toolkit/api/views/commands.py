"""
API ViewSet for Command resources
"""
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction
from drf_spectacular.utils import extend_schema_view
from dcim.models import Device
from netbox.api.viewsets import NetBoxModelViewSet

from ... import models, filtersets
from ...services.command_service import CommandExecutionService
from ...services.rate_limiting_service import RateLimitingService
from ..serializers import CommandSerializer, CommandExecutionSerializer
from ..mixins import APIResponseMixin, PermissionCheckMixin
from ..schemas import (
    COMMAND_LIST_SCHEMA,
    COMMAND_RETRIEVE_SCHEMA,
    COMMAND_CREATE_SCHEMA,
    COMMAND_UPDATE_SCHEMA,
    COMMAND_PARTIAL_UPDATE_SCHEMA,
    COMMAND_DESTROY_SCHEMA,
    COMMAND_EXECUTE_SCHEMA,
    COMMAND_BULK_EXECUTE_SCHEMA,
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
    
    @COMMAND_EXECUTE_SCHEMA
    @action(detail=True, methods=['post'], url_path='execute')
    def execute_command(self, request, pk=None):
        """Execute a command on a device via API"""
        command = self.get_object()
        
        # Validate input using serializer
        execution_serializer = CommandExecutionSerializer(data=request.data)
        if not execution_serializer.is_valid():
            return Response(
                {
                    'error': 'Invalid input data',
                    'details': execution_serializer.errors
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        validated_data = execution_serializer.validated_data
        device_id = validated_data['device_id']
        username = validated_data['username']
        password = validated_data['password']
        
        # Get device object
        try:
            device = Device.objects.get(id=device_id)
        except Device.DoesNotExist:
            return Response(
                {'error': f'Device with ID {device_id} not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check permissions based on command type using NetBox's object-based permissions
        if command.command_type == 'config':
            if not self._user_has_action_permission(request.user, command, 'execute_config'):
                return Response(
                    {'error': 'You do not have permission to execute configuration commands'}, 
                    status=status.HTTP_403_FORBIDDEN
                )
        elif command.command_type == 'show':
            if not self._user_has_action_permission(request.user, command, 'execute_show'):
                return Response(
                    {'error': 'You do not have permission to execute show commands'}, 
                    status=status.HTTP_403_FORBIDDEN
                )
        
        # Check custom rate limiting (device-specific with bypass rules)
        rate_limiting_service = RateLimitingService()
        rate_limit_check = rate_limiting_service.check_rate_limit(device, request.user)
        
        if not rate_limit_check['allowed']:
            return Response(
                {
                    'error': 'Rate limit exceeded',
                    'details': {
                        'reason': rate_limit_check['reason'],
                        'current_count': rate_limit_check['current_count'],
                        'limit': rate_limit_check['limit'],
                        'time_window_minutes': rate_limit_check['time_window_minutes']
                    }
                },
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )
        
        # Execute command using the service
        command_service = CommandExecutionService()
        result = command_service.execute_command_with_retry(
            command, device, username, password, max_retries=1
        )
        
        # Determine overall success - failed if either execution failed or syntax error detected
        overall_success = result.success and not result.has_syntax_error
        
        # Prepare response data
        response_data = {
            'success': overall_success,
            'output': result.output,
            'error_message': result.error_message,
            'execution_time': result.execution_time,
            'command': {
                'id': command.id,
                'name': command.name,
                'command_type': command.command_type
            },
            'device': {
                'id': device.id,
                'name': device.name
            }
        }
        
        # Add syntax error information if detected
        if result.has_syntax_error:
            response_data['syntax_error'] = {
                'detected': True,
                'type': result.syntax_error_type,
                'vendor': result.syntax_error_vendor,
                'guidance_provided': True
            }
        else:
            response_data['syntax_error'] = {
                'detected': False
            }
        
        # Add parsing information if available
        if result.parsing_success and result.parsed_output:
            response_data['parsed_output'] = {
                'success': True,
                'method': result.parsing_method,
                'data': result.parsed_output
            }
        else:
            response_data['parsed_output'] = {
                'success': False,
                'method': None,
                'error': result.parsing_error
            }
        
        # Return appropriate status code
        status_code = status.HTTP_200_OK if overall_success else status.HTTP_400_BAD_REQUEST
        
        return Response(response_data, status=status_code)
    
    @COMMAND_BULK_EXECUTE_SCHEMA
    @action(detail=False, methods=['post'], url_path='bulk-execute')
    def bulk_execute(self, request):
        """Execute multiple commands on multiple devices"""
        executions = request.data.get('executions', [])
        
        if not executions:
            return Response(
                {'error': 'No executions provided'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        results = []
        
        with transaction.atomic():
            for i, execution_data in enumerate(executions):
                try:
                    # Validate each execution
                    command_id = execution_data.get('command_id')
                    device_id = execution_data.get('device_id')
                    username = execution_data.get('username')
                    password = execution_data.get('password')
                    
                    if not all([command_id, device_id, username, password]):
                        results.append({
                            'execution_id': i + 1,
                            'success': False,
                            'error': 'Missing required fields'
                        })
                        continue
                    
                    # Get command and device objects
                    try:
                        command = models.Command.objects.get(id=command_id)
                        device = Device.objects.get(id=device_id)
                    except (models.Command.DoesNotExist, Device.DoesNotExist) as e:
                        results.append({
                            'execution_id': i + 1,
                            'success': False,
                            'error': f'Object not found: {str(e)}'
                        })
                        continue
                    
                    # Check permissions
                    action = 'execute_config' if command.command_type == 'config' else 'execute_show'
                    if not self._user_has_action_permission(request.user, command, action):
                        results.append({
                            'execution_id': i + 1,
                            'success': False,
                            'error': 'Insufficient permissions'
                        })
                        continue
                    
                    # Execute command
                    command_service = CommandExecutionService()
                    result = command_service.execute_command_with_retry(
                        command, device, username, password, max_retries=1
                    )
                    
                    # Create command log entry (this would typically be done by the service)
                    log_entry = models.CommandLog.objects.create(
                        command=command,
                        device=device,
                        user=request.user,
                        output=result.output,
                        error_message=result.error_message,
                        execution_time=result.execution_time,
                        success=result.success and not result.has_syntax_error
                    )
                    
                    results.append({
                        'execution_id': i + 1,
                        'success': result.success and not result.has_syntax_error,
                        'command_log_id': log_entry.id,
                        'execution_time': result.execution_time
                    })
                    
                except Exception as e:
                    results.append({
                        'execution_id': i + 1,
                        'success': False,
                        'error': f'Unexpected error: {str(e)}'
                    })
        
        # Generate summary
        total = len(results)
        successful = sum(1 for r in results if r.get('success', False))
        failed = total - successful
        
        return Response({
            'results': results,
            'summary': {
                'total': total,
                'successful': successful,
                'failed': failed
            }
        }, status=status.HTTP_200_OK)
