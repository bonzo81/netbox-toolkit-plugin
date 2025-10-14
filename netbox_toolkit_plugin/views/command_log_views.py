"""Command log related views for the NetBox Toolkit Plugin."""

import csv
from datetime import timedelta

from django.db.models import Count, Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django.views import View
from django.views.generic import TemplateView

from netbox.views.generic import (
    ObjectDeleteView,
    ObjectEditView,
    ObjectListView,
    ObjectView,
)

from ..models import CommandLog


class CommandLogListView(ObjectListView):
    queryset = CommandLog.objects.all()
    filterset = None  # Will update this after import
    table = None  # Will update this after import
    template_name = "netbox_toolkit_plugin/commandlog_list.html"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from ..filtersets import CommandLogFilterSet
        from ..tables import CommandLogTable

        self.filterset = CommandLogFilterSet
        self.table = CommandLogTable

    def get_extra_context(self, request):
        """Override to disable 'Add' button since logs are created automatically"""
        context = super().get_extra_context(request)
        context["add_button_url"] = None  # Disable the add button
        return context


class CommandLogView(ObjectView):
    queryset = CommandLog.objects.all()
    template_name = "netbox_toolkit_plugin/commandlog.html"


class CommandLogEditView(ObjectEditView):
    queryset = CommandLog.objects.all()
    form = None  # No form since we don't want manual editing
    template_name = "netbox_toolkit_plugin/commandlog_edit.html"

    def get(self, request, *args, **kwargs):
        # Redirect to the detail view since we don't allow editing
        if "pk" in kwargs:
            return redirect(
                "plugins:netbox_toolkit_plugin:commandlog_view", pk=kwargs["pk"]
            )
        return redirect("plugins:netbox_toolkit_plugin:commandlog_list")


class CommandLogDeleteView(ObjectDeleteView):
    queryset = CommandLog.objects.all()


class CommandLogExportCSVView(View):
    """Django view for downloading CommandLog parsed data as CSV file"""

    def get(self, request, pk):
        """Export parsed command log data as CSV file"""
        command_log = get_object_or_404(CommandLog, pk=pk)

        # Parse the command output on-demand using the same logic as the API
        try:
            # Import textfsm parser
            from ntc_templates.parse import parse_output

            # Get the device platform for parsing and use centralized normalization
            platform_slug = (
                command_log.device.platform.slug
                if command_log.device.platform
                else "generic"
            )

            # Use centralized platform normalization (single source of truth)
            from ..settings import ToolkitSettings

            device_platform = ToolkitSettings.normalize_platform(platform_slug)

            # Try to parse the stored output using ntc-templates
            parsed_result = parse_output(
                platform=device_platform,
                command=command_log.command.command,
                data=command_log.output,
            )

            if not parsed_result or not isinstance(parsed_result, list):
                return HttpResponse(
                    "No parsed data available for this command log. The output could not be parsed into structured data.",
                    status=404,
                )

            parsed_data = parsed_result

            if not isinstance(parsed_data, list) or len(parsed_data) == 0:
                return HttpResponse(
                    "Parsed data is not in a valid CSV format (must be a non-empty list).",
                    status=400,
                )

            # Generate filename
            filename = f"{command_log.command.name}_{command_log.device.name}_{command_log.execution_time.strftime('%Y%m%d_%H%M%S')}.csv"

            # Create CSV response
            response = HttpResponse(content_type="text/csv")
            response["Content-Disposition"] = f'attachment; filename="{filename}"'

            writer = csv.writer(response)

            # Handle list of objects (most common case)
            if isinstance(parsed_data[0], dict):
                # Write headers
                headers = list(parsed_data[0].keys())
                writer.writerow(headers)

                # Write data rows
                for row in parsed_data:
                    writer.writerow([row.get(header, "") for header in headers])
            else:
                # Handle simple list
                for item in parsed_data:
                    writer.writerow([str(item)])

            return response

        except Exception as e:
            return HttpResponse(
                f"Failed to parse command output or generate CSV: {str(e)}", status=400
            )


class ToolkitStatisticsView(TemplateView):
    """View for displaying command execution statistics dashboard"""

    template_name = "netbox_toolkit_plugin/toolkit_stats.html"

    def get_context_data(self, **kwargs):
        """Get statistics data for the template"""
        context = super().get_context_data(**kwargs)

        # Get all command logs
        queryset = CommandLog.objects.all()

        # Basic stats
        total_logs = queryset.count()
        successful_logs = queryset.filter(success=True).count()
        success_rate = (successful_logs / total_logs * 100) if total_logs > 0 else 0

        # Last 24 hours stats
        last_24h = timezone.now() - timedelta(hours=24)
        recent_logs = queryset.filter(execution_time__gte=last_24h)
        recent_total = recent_logs.count()
        recent_successful = recent_logs.filter(success=True).count()
        recent_failed = recent_total - recent_successful

        # Top commands
        top_commands = (
            queryset.values("command__name")
            .annotate(count=Count("command"))
            .order_by("-count")[:10]
        )

        # Common errors (non-empty error messages)
        common_errors = (
            queryset.filter(~Q(error_message=""), ~Q(error_message__isnull=True))
            .values("error_message")
            .annotate(count=Count("error_message"))
            .order_by("-count")[:10]
        )

        # Add data to context
        context.update({
            "total_logs": total_logs,
            "success_rate": round(success_rate, 2),
            "last_24h": {
                "total": recent_total,
                "successful": recent_successful,
                "failed": recent_failed,
            },
            "top_commands": [
                {"command_name": item["command__name"], "count": item["count"]}
                for item in top_commands
            ],
            "common_errors": [
                {"error": item["error_message"][:100], "count": item["count"]}
                for item in common_errors
            ],
        })

        return context
