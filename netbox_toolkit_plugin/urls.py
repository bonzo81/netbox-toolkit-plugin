from django.urls import path

from . import views

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
    # Device toolkit view
    path(
        "devices/<int:pk>/toolkit/",
        views.DeviceToolkitView.as_view(),
        name="device_toolkit",
    ),
]
