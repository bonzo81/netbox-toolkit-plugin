"""
NetBox Toolkit Plugin Views

This package contains all view classes for the NetBox Toolkit Plugin,
organized by functionality for better maintainability.
"""

# Import all view classes to maintain backward compatibility
from .command_log_views import (
    CommandLogDeleteView,
    CommandLogEditView,
    CommandLogExportCSVView,
    CommandLogListView,
    CommandLogView,
)
from .command_views import (
    CommandChangeLogView,
    CommandDeleteView,
    CommandEditView,
    CommandListView,
    CommandVariableFormView,
    CommandView,
)
from .device_views import (
    DeviceCommandOutputView,
    DeviceExecutionModalView,
    DeviceRateLimitUpdateView,
    DeviceRecentHistoryView,
    DeviceToolkitView,
)

__all__ = [
    # Device Views
    "DeviceToolkitView",
    "DeviceExecutionModalView",
    "DeviceRateLimitUpdateView",
    "DeviceCommandOutputView",
    "DeviceRecentHistoryView",
    # Command Views
    "CommandListView",
    "CommandEditView",
    "CommandVariableFormView",
    "CommandView",
    "CommandDeleteView",
    "CommandChangeLogView",
    # Command Log Views
    "CommandLogListView",
    "CommandLogView",
    "CommandLogEditView",
    "CommandLogDeleteView",
    "CommandLogExportCSVView",
]
