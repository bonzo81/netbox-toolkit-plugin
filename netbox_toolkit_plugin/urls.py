from django.urls import path

from netbox.views.generic import ObjectChangeLogView

from . import models, views

app_name = "netbox_toolkit_plugin"

urlpatterns = [
    # Command views
    path("commands/", views.CommandListView.as_view(), name="command_list"),
    path("commands/add/", views.CommandEditView.as_view(), name="command_add"),
    path("commands/<int:pk>/", views.CommandView.as_view(), name="command_detail"),
    path(
        "commands/<int:pk>/edit/", views.CommandEditView.as_view(), name="command_edit"
    ),
    path(
        "commands/<int:pk>/delete/",
        views.CommandDeleteView.as_view(),
        name="command_delete",
    ),
    path(
        "commands/<int:pk>/changelog/",
        views.CommandChangeLogView.as_view(),
        name="command_changelog",
    ),
    # HTMX endpoints
    path(
        "commands/<int:pk>/add-variable/",
        views.CommandVariableFormView.as_view(),
        name="command_add_variable",
    ),
    # Command Log views
    path("logs/", views.CommandLogListView.as_view(), name="commandlog_list"),
    path("logs/add/", views.CommandLogEditView.as_view(), name="commandlog_add"),
    path("logs/<int:pk>/", views.CommandLogView.as_view(), name="commandlog_view"),
    path(
        "logs/<int:pk>/edit/",
        views.CommandLogEditView.as_view(),
        name="commandlog_edit",
    ),
    path(
        "logs/<int:pk>/delete/",
        views.CommandLogDeleteView.as_view(),
        name="commandlog_delete",
    ),
    path(
        "logs/<int:pk>/changelog/",
        ObjectChangeLogView.as_view(),
        name="commandlog_changelog",
        kwargs={"model": models.CommandLog},
    ),
    path(
        "logs/<int:pk>/export-csv/",
        views.CommandLogExportCSVView.as_view(),
        name="commandlog_export_csv",
    ),
    # Device toolkit view
    path(
        "devices/<int:pk>/toolkit/",
        views.DeviceToolkitView.as_view(),
        name="device_toolkit",
    ),
    # HTMX endpoints for device toolkit
    path(
        "devices/<int:pk>/execution-modal/",
        views.DeviceExecutionModalView.as_view(),
        name="device_execution_modal",
    ),
    path(
        "devices/<int:pk>/rate-limit-update/",
        views.DeviceRateLimitUpdateView.as_view(),
        name="rate_limit_update",
    ),
    path(
        "devices/<int:pk>/command-output/",
        views.DeviceCommandOutputView.as_view(),
        name="command_output_update",
    ),
    path(
        "devices/<int:pk>/recent-history/",
        views.DeviceRecentHistoryView.as_view(),
        name="recent_history_update",
    ),
    # Device Credential Set views
    path(
        "credentials/",
        views.DeviceCredentialSetListView.as_view(),
        name="devicecredentialset_list",
    ),
    path(
        "credentials/add/",
        views.DeviceCredentialSetCreateView.as_view(),
        name="devicecredentialset_add",
    ),
    path(
        "credentials/<int:pk>/",
        views.DeviceCredentialSetDetailView.as_view(),
        name="devicecredentialset_detail",
    ),
    path(
        "credentials/<int:pk>/edit/",
        views.DeviceCredentialSetEditView.as_view(),
        name="devicecredentialset_edit",
    ),
    path(
        "credentials/<int:pk>/delete/",
        views.DeviceCredentialSetDeleteView.as_view(),
        name="devicecredentialset_delete",
    ),
    path(
        "credentials/<int:pk>/regenerate-token/",
        views.RegenerateTokenView.as_view(),
        name="devicecredentialset_regenerate_token",
    ),
    path(
        "credentials/<int:pk>/token-modal/",
        views.DeviceCredentialSetTokenModalView.as_view(),
        name="devicecredentialset_token_modal",
    ),
    path(
        "credentials/<int:pk>/changelog/",
        views.DeviceCredentialSetChangeLogView.as_view(),
        name="devicecredentialset_changelog",
        kwargs={"model": models.DeviceCredentialSet},
    ),
    # Statistics dashboard
    path("stats/", views.ToolkitStatisticsView.as_view(), name="toolkit_stats"),
]
