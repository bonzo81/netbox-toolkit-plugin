from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.views.generic import DetailView

from netbox.views.generic import (
    BulkDeleteView,
    BulkEditView,
    BulkImportView,
    ObjectChangeLogView,
    ObjectDeleteView,
    ObjectEditView,
    ObjectListView,
    ObjectView,
)

from ..filtersets import DeviceCredentialSetFilterSet
from ..forms import DeviceCredentialSetForm
from ..models import DeviceCredentialSet
from ..tables import DeviceCredentialSetTable


class DeviceCredentialSetListView(ObjectListView):
    """List view for device credential sets - users see only their own."""

    queryset = DeviceCredentialSet.objects.all()
    filterset = None  # Will update this after import
    table = None  # Will update this after import

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from ..filtersets import DeviceCredentialSetFilterSet
        from ..tables import DeviceCredentialSetTable

        self.filterset = DeviceCredentialSetFilterSet
        self.table = DeviceCredentialSetTable

    def get_queryset(self, request):
        # Users can only see their own credential sets
        return super().get_queryset(request).filter(owner=request.user)


class DeviceCredentialSetDetailView(ObjectView):
    """Detail view for device credential sets."""

    queryset = DeviceCredentialSet.objects.all()

    def get_queryset(self, request):
        # Users can only view their own credential sets
        return super().get_queryset(request).filter(owner=request.user)

    def get_extra_context(self, request, instance):
        # Add usage statistics and related information
        return {
            "platform_count": instance.platforms.count(),
            "last_used_display": instance.last_used.strftime("%Y-%m-%d %H:%M")
            if instance.last_used
            else "Never",
        }


class DeviceCredentialSetCreateView(ObjectEditView):
    """Create view for device credential sets."""

    queryset = DeviceCredentialSet.objects.all()
    form = DeviceCredentialSetForm

    def post(self, request, *args, **kwargs):
        # Create form directly with request data and user
        form = self.form(data=request.POST, files=request.FILES, user=request.user)

        if form.is_valid():
            # Set the owner before calling form.save()
            if not form.instance.pk:
                form.instance.owner = request.user

            # Now save the form
            obj = form.save()

            # Handle success messages - always redirect to credentials page for token access
            if hasattr(form, "_new_credential_token"):
                messages.success(
                    request,
                    f"Credential set '{obj.name}' created successfully. "
                    "Your credential token is available on the credentials page.",
                )
            else:
                messages.success(
                    request,
                    f"Credential set '{obj.name}' created successfully.",
                )

            # Redirect to list page
            return redirect("plugins:netbox_toolkit_plugin:devicecredentialset_list")
        else:
            # For invalid forms, render with errors using simple pattern like edit view
            from django.shortcuts import render

            return render(
                request,
                "netbox_toolkit_plugin/devicecredentialset_edit.html",  # Use same template as edit
                {
                    "object": None,
                    "form": form,
                },
            )


class DeviceCredentialSetEditView(ObjectEditView):
    """Edit view for device credential sets."""

    queryset = DeviceCredentialSet.objects.all()
    form = DeviceCredentialSetForm
    template_name = "netbox_toolkit_plugin/devicecredentialset_edit.html"

    def get_queryset(self, request):
        # Users can only edit their own credential sets
        qs = super().get_queryset(request).filter(owner=request.user)
        return qs

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        # Get the object being edited - FIXED: Get the actual instance from the database
        pk = self.kwargs.get("pk")

        try:
            # Direct query with ownership filtering to ensure we get the actual object
            self.object = DeviceCredentialSet.objects.get(pk=pk, owner=request.user)
        except DeviceCredentialSet.DoesNotExist:
            messages.error(
                request,
                "Credential set not found or you don't have permission to edit it.",
            )
            return redirect("plugins:netbox_toolkit_plugin:devicecredentialset_list")

        # Create form with proper user context and instance
        form = self.form(
            data=request.POST,
            files=request.FILES,
            instance=self.object,
            user=request.user,
        )

        if form.is_valid():
            # Save the form
            self.object = form.save()

            # Handle success messages - always redirect to credentials page for token access
            if hasattr(form, "_new_credential_token"):
                messages.success(
                    self.request,
                    f"Credential set '{form.instance.name}' updated successfully. "
                    "Your credential token is available on the credentials page.",
                )
            else:
                messages.success(
                    self.request,
                    f"Credential set '{form.instance.name}' updated successfully.",
                )
            # Redirect to the credential list page
            return redirect("plugins:netbox_toolkit_plugin:devicecredentialset_list")
        else:
            # For invalid forms, render with errors using simple pattern like CommandEditView
            from django.shortcuts import render

            return render(
                request,
                "netbox_toolkit_plugin/devicecredentialset_edit.html",  # Custom template for credential edit
                {
                    "object": self.object,
                    "form": form,
                },
            )

    def get_success_url(self):
        """Return URL to redirect to after successful edit."""
        return "plugins:netbox_toolkit_plugin:devicecredentialset_list"

    def get_form(self, form_class=None):
        # If we have a form with errors from a failed POST, use it
        if hasattr(self, "_form_with_errors"):
            form = self._form_with_errors
            # Clean up
            delattr(self, "_form_with_errors")
            return form

        form_class = form_class or self.form
        kwargs = self.get_form_kwargs()
        kwargs["user"] = self.request.user
        form = form_class(**kwargs)
        return form

    def form_valid(self, form):
        # Save the form first
        super().form_valid(form)

        if hasattr(form, "_new_credential_token"):
            messages.success(
                self.request,
                f"Credential set '{form.instance.name}' updated successfully. "
                f"Your new credential token is: <code>{form._new_credential_token}</code><br>"
                f"<strong>⚠️ Important:</strong> Copy this token now - it won't be shown again!",
                extra_tags="safe",  # Allow HTML in message
            )
        else:
            messages.success(
                self.request,
                f"Credential set '{form.instance.name}' updated successfully.",
            )
        return super().form_valid(form)


class DeviceCredentialSetDeleteView(ObjectDeleteView):
    """Delete view for device credential sets."""

    queryset = DeviceCredentialSet.objects.select_related("owner").prefetch_related(
        "platforms"
    )

    def dispatch(self, request, *args, **kwargs):
        # Filter the queryset to only include user's own credential sets
        self.queryset = self.queryset.filter(owner=request.user)
        return super().dispatch(request, *args, **kwargs)


class DeviceCredentialSetBulkImportView(BulkImportView):
    """Bulk import view for device credential sets."""

    queryset = DeviceCredentialSet.objects.all()
    model_form = DeviceCredentialSetForm

    def get_queryset(self, request):
        # Users can only import into their own account
        return super().get_queryset(request).filter(owner=request.user)


class DeviceCredentialSetBulkEditView(BulkEditView):
    """Bulk edit view for device credential sets."""

    queryset = DeviceCredentialSet.objects.all()
    filterset_class = DeviceCredentialSetFilterSet
    table = DeviceCredentialSetTable
    form = DeviceCredentialSetForm  # You might want a separate bulk edit form

    def get_queryset(self, request):
        # Users can only bulk edit their own credential sets
        return super().get_queryset(request).filter(owner=request.user)


class DeviceCredentialSetBulkDeleteView(BulkDeleteView):
    """Bulk delete view for device credential sets."""

    queryset = DeviceCredentialSet.objects.all()
    filterset_class = DeviceCredentialSetFilterSet
    table = DeviceCredentialSetTable

    def dispatch(self, request, *args, **kwargs):
        # Filter the queryset to only include user's own credential sets
        self.queryset = self.queryset.filter(owner=request.user)
        return super().dispatch(request, *args, **kwargs)


# Additional view for regenerating credential tokens
class RegenerateTokenView(LoginRequiredMixin, DetailView):
    """View to regenerate credential token for a credential set."""

    model = DeviceCredentialSet
    template_name = "netbox_toolkit_plugin/devicecredentialset_regenerate_token.html"

    def get_queryset(self):
        return DeviceCredentialSet.objects.filter(owner=self.request.user)

    def post(self, request, *args, **kwargs):
        """Handle token regeneration with confirmation."""
        credential_set = self.get_object()

        # Check for confirmation
        if request.POST.get("confirm") != "REGENERATE":
            messages.error(
                request,
                'Token regeneration cancelled. You must type "REGENERATE" exactly to confirm.',
            )
            return redirect(request.path)

        # Import here to avoid circular imports
        from ..services.credential_service import CredentialService

        credential_service = CredentialService()

        # Regenerate token using the proper service method
        success, new_token, error = credential_service.regenerate_token(
            credential_set.id, request.user
        )

        if success:
            # Add success message with secure token display
            from django.utils.safestring import mark_safe

            message = mark_safe(
                f"Credential token for '{credential_set.name}' has been regenerated.<br><br>"
                f"<strong>Your new credential token:</strong><br>"
                f"<div class='alert alert-info mt-2 mb-2'>"
                f"<code style='font-size: 0.9em; word-break: break-all;'>{new_token}</code>"
                f"</div>"
                f"<div class='alert alert-warning mt-2'>"
                f"<i class='mdi mdi-alert'></i> <strong>Important:</strong> Copy this token now - it won't be shown again!"
                f"</div>"
            )
            messages.success(request, message)
        else:
            # Add sanitized error message
            messages.error(
                request,
                f"Failed to regenerate token for '{credential_set.name}'. Please try again.",
            )

        # Redirect to list page
        return redirect("plugins:netbox_toolkit_plugin:devicecredentialset_list")


class DeviceCredentialSetTokenModalView(LoginRequiredMixin, DetailView):
    """HTMX view for displaying token reveal modal."""

    model = DeviceCredentialSet
    template_name = "netbox_toolkit_plugin/htmx/token_modal.html"
    context_object_name = "credential_set"

    def get_queryset(self):
        # Users can only view their own credential sets
        return DeviceCredentialSet.objects.filter(owner=self.request.user)


class DeviceCredentialSetChangeLogView(ObjectChangeLogView):
    """
    Changelog view for device credential sets with ownership filtering.
    Users can only view the changelog for their own credential sets.
    """

    def get_queryset(self, request):
        """
        Filter the base queryset to only include credential sets owned by the current user.
        This ensures users cannot view changelog entries for other users' credentials.
        """
        # Get the base queryset (will be filtered by the primary key from URL)
        base_queryset = super().get_queryset(request)
        # Add ownership filtering to restrict access to only user's own credentials
        return base_queryset.filter(owner=request.user)
