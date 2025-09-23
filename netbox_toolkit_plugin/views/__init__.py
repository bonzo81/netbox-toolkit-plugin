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
from .credential_views import (
    DeviceCredentialSetCreateView,
    DeviceCredentialSetDeleteView,
    DeviceCredentialSetDetailView,
    DeviceCredentialSetEditView,
    DeviceCredentialSetListView,
    DeviceCredentialSetShowTokenView,
    DeviceCredentialSetTokenModalView,
    RegenerateTokenView,
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
    "CommandView",
    "CommandEditView",
    "CommandDeleteView",
    "CommandVariableFormView",
    "CommandChangeLogView",
    # Command Log Views
    "CommandLogListView",
    "CommandLogView",
    "CommandLogEditView",
    "CommandLogDeleteView",
    "CommandLogExportCSVView",
    # Device Credential Set Views
    "DeviceCredentialSetListView",
    "DeviceCredentialSetDetailView",
    "DeviceCredentialSetCreateView",
    "DeviceCredentialSetEditView",
    "DeviceCredentialSetDeleteView",
    "DeviceCredentialSetTokenModalView",
    "RegenerateTokenView",
]
