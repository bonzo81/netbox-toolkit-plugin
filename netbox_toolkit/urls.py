from django.urls import path
from . import views

app_name = 'netbox_toolkit'

urlpatterns = [
    # Command views
    path('commands/', views.CommandListView.as_view(), name='command_list'),
    path('commands/add/', views.CommandEditView.as_view(), name='command_add'),
    path('commands/<int:pk>/', views.CommandView.as_view(), name='command_detail'),
    path('commands/<int:pk>/edit/', views.CommandEditView.as_view(), name='command_edit'),
    path('commands/<int:pk>/delete/', views.CommandDeleteView.as_view(), name='command_delete'),
    path('commands/<int:pk>/changelog/', views.CommandChangeLogView.as_view(), name='command_changelog'),
    
    # Command Log views
    path('logs/', views.CommandLogListView.as_view(), name='commandlog_list'),
    path('logs/<int:pk>/', views.CommandLogView.as_view(), name='commandlog_view'),
    path('logs/<int:pk>/changelog/', views.CommandLogChangeLogView.as_view(), name='commandlog_changelog'),
    
    # Device toolkit view
    path('devices/<int:pk>/toolkit/', views.DeviceToolkitView.as_view(), name='device_toolkit'),
]