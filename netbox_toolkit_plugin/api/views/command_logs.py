"""
API ViewSet for CommandLog resources
"""
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from datetime import timedelta
from django.db.models import Count, Q
from django.http import HttpResponse
from drf_spectacular.utils import extend_schema_view
from netbox.api.viewsets import NetBoxModelViewSet

from ... import models, filtersets
from ..serializers import CommandLogSerializer
from ..mixins import APIResponseMixin
from ..schemas import (
    COMMAND_LOG_LIST_SCHEMA,
    COMMAND_LOG_RETRIEVE_SCHEMA,
    COMMAND_LOG_CREATE_SCHEMA,
    COMMAND_LOG_UPDATE_SCHEMA,
    COMMAND_LOG_PARTIAL_UPDATE_SCHEMA,
    COMMAND_LOG_DESTROY_SCHEMA,
    COMMAND_LOG_STATISTICS_SCHEMA,
    COMMAND_LOG_EXPORT_SCHEMA,
)


@extend_schema_view(
    list=COMMAND_LOG_LIST_SCHEMA,
    retrieve=COMMAND_LOG_RETRIEVE_SCHEMA,
    create=COMMAND_LOG_CREATE_SCHEMA,
    update=COMMAND_LOG_UPDATE_SCHEMA,
    partial_update=COMMAND_LOG_PARTIAL_UPDATE_SCHEMA,
    destroy=COMMAND_LOG_DESTROY_SCHEMA,
)
class CommandLogViewSet(NetBoxModelViewSet, APIResponseMixin):
    queryset = models.CommandLog.objects.all()
    serializer_class = CommandLogSerializer
    filterset_class = filtersets.CommandLogFilterSet
    # NetBox automatically handles object-based permissions - no need for explicit permission_classes
    
    def get_queryset(self):
        """NetBox will automatically filter based on user's ObjectPermissions"""
        return super().get_queryset()
    
    @COMMAND_LOG_STATISTICS_SCHEMA
    @action(detail=False, methods=['get'], url_path='statistics')
    def statistics(self, request):
        """Get command execution statistics"""
        queryset = self.get_queryset()
        
        # Basic stats
        total_logs = queryset.count()
        successful_logs = queryset.filter(success=True).count()
        success_rate = (successful_logs / total_logs * 100) if total_logs > 0 else 0
        
        # Last 24 hours stats
        last_24h = timezone.now() - timedelta(hours=24)
        recent_logs = queryset.filter(created__gte=last_24h)
        recent_total = recent_logs.count()
        recent_successful = recent_logs.filter(success=True).count()
        recent_failed = recent_total - recent_successful
        
        # Top commands
        top_commands = (
            queryset.values('command__name')
            .annotate(count=Count('command'))
            .order_by('-count')[:10]
        )
        
        # Common errors (non-empty error messages)
        common_errors = (
            queryset.filter(~Q(error_message=''), ~Q(error_message__isnull=True))
            .values('error_message')
            .annotate(count=Count('error_message'))
            .order_by('-count')[:10]
        )
        
        return Response({
            'total_logs': total_logs,
            'success_rate': round(success_rate, 2),
            'last_24h': {
                'total': recent_total,
                'successful': recent_successful,
                'failed': recent_failed
            },
            'top_commands': [
                {'command_name': item['command__name'], 'count': item['count']}
                for item in top_commands
            ],
            'common_errors': [
                {'error': item['error_message'][:100], 'count': item['count']}
                for item in common_errors
            ]
        })
    
    @COMMAND_LOG_EXPORT_SCHEMA
    @action(detail=False, methods=['get'], url_path='export')
    def export(self, request):
        """Export command logs"""
        import csv
        from datetime import datetime
        
        export_format = request.query_params.get('format', 'json')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        queryset = self.get_queryset()
        
        # Apply date filters if provided
        if start_date:
            try:
                start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
                queryset = queryset.filter(created__date__gte=start_date)
            except ValueError:
                return Response(
                    {'error': 'Invalid start_date format. Use YYYY-MM-DD.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        if end_date:
            try:
                end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
                queryset = queryset.filter(created__date__lte=end_date)
            except ValueError:
                return Response(
                    {'error': 'Invalid end_date format. Use YYYY-MM-DD.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Limit export size for performance
        if queryset.count() > 10000:
            return Response(
                {'error': 'Export too large. Please use date filters to reduce size.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if export_format == 'csv':
            # CSV export
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="command_logs.csv"'
            
            writer = csv.writer(response)
            writer.writerow([
                'ID', 'Command', 'Device', 'User', 'Success', 
                'Created', 'Execution Time', 'Error Message'
            ])
            
            for log in queryset.select_related('command', 'device', 'user'):
                writer.writerow([
                    log.id,
                    log.command.name,
                    log.device.name,
                    log.user.username if log.user else 'Unknown',
                    log.success,
                    log.created.isoformat(),
                    log.execution_time,
                    log.error_message or ''
                ])
            
            return response
        
        else:
            # JSON export
            serializer = self.get_serializer(queryset, many=True)
            return Response({
                'count': queryset.count(),
                'results': serializer.data
            })
