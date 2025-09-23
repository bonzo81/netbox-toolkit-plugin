"""
Views for managing device credential sets.
These views provide GUI-based CRUD operations for secure credential storage.
"""

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.views.generic import (
    DetailView,
)

from netbox.views import generic

from ..filtersets import DeviceCredentialSetFilterSet
from ..forms import DeviceCredentialSetForm
from ..models import DeviceCredentialSet
from ..tables import DeviceCredentialSetTable


class DeviceCredentialSetListView(generic.ObjectListView):
    """List view for device credential sets - users see only their own."""

    queryset = DeviceCredentialSet.objects.all()
    filterset_class = DeviceCredentialSetFilterSet
    table = DeviceCredentialSetTable

    def get_queryset(self, request):
        # Users can only see their own credential sets
        return super().get_queryset(request).filter(owner=request.user)


class DeviceCredentialSetDetailView(generic.ObjectView):
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


class DeviceCredentialSetCreateView(generic.ObjectEditView):
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

            # Add success message
            messages.success(
                request,
                f"Credential set '{obj.name}' created successfully. "
                f"You can view the credential token from the credentials list.",
            )

            # Redirect to list page
            return redirect("plugins:netbox_toolkit_plugin:devicecredentialset_list")
        else:
            # For invalid forms, render the form with errors
            context = self.get_context_data()
            context["form"] = form
            return self.render_to_response(context)


class DeviceCredentialSetEditView(generic.ObjectEditView):
    """Edit view for device credential sets."""

    queryset = DeviceCredentialSet.objects.all()
    form = DeviceCredentialSetForm

    def get_queryset(self, request):
        # Users can only edit their own credential sets
        return super().get_queryset(request).filter(owner=request.user)

    def get_form(self, form_class=None):
        form_class = form_class or self.form
        kwargs = self.get_form_kwargs()
        kwargs["user"] = self.request.user
        return form_class(**kwargs)

    def form_valid(self, form):
        # Check if password was changed and show new token if so
        if form.cleaned_data.get("password"):
            messages.success(
                self.request,
                f"Credential set '{form.instance.name}' updated successfully. "
                f"New credential token: {form.instance.access_token[:20]}... (save this token securely)",
            )
        else:
            messages.success(
                self.request,
                f"Credential set '{form.instance.name}' updated successfully.",
            )
        return super().form_valid(form)


class DeviceCredentialSetDeleteView(generic.ObjectDeleteView):
    """Delete view for device credential sets."""

    queryset = DeviceCredentialSet.objects.select_related("owner").prefetch_related(
        "platforms"
    )

    def dispatch(self, request, *args, **kwargs):
        # Filter the queryset to only include user's own credential sets
        self.queryset = self.queryset.filter(owner=request.user)
        return super().dispatch(request, *args, **kwargs)


class DeviceCredentialSetBulkImportView(generic.BulkImportView):
    """Bulk import view for device credential sets."""

    queryset = DeviceCredentialSet.objects.all()
    model_form = DeviceCredentialSetForm

    def get_queryset(self, request):
        # Users can only import into their own account
        return super().get_queryset(request).filter(owner=request.user)


class DeviceCredentialSetBulkEditView(generic.BulkEditView):
    """Bulk edit view for device credential sets."""

    queryset = DeviceCredentialSet.objects.all()
    filterset_class = DeviceCredentialSetFilterSet
    table = DeviceCredentialSetTable
    form = DeviceCredentialSetForm  # You might want a separate bulk edit form

    def get_queryset(self, request):
        # Users can only bulk edit their own credential sets
        return super().get_queryset(request).filter(owner=request.user)


class DeviceCredentialSetBulkDeleteView(generic.BulkDeleteView):
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
        from ..services.encryption_service import CredentialEncryptionService

        encryption_service = CredentialEncryptionService()

        # Generate new token
        credential_set.access_token = encryption_service.generate_access_token()
        credential_set.save(update_fields=["access_token"])

        # Add success message
        messages.success(
            request,
            f"Credential token for '{credential_set.name}' has been regenerated. "
            f"You can view it from the credentials list.",
        )

        # Redirect to list page
        return redirect("plugins:netbox_toolkit_plugin:devicecredentialset_list")


class DeviceCredentialSetShowTokenView(generic.ObjectView):
    """View for displaying the credential token one time after creation/regeneration."""

    queryset = DeviceCredentialSet.objects.all()
    template_name = "netbox_toolkit_plugin/devicecredentialset_show_token.html"

    def get_queryset(self, request):
        return DeviceCredentialSet.objects.filter(owner=request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get token data from session
        token_data = self.request.session.get("credential_token", None)

        # Debug information
        print(f"DEBUG TOKEN DISPLAY: token_data = {token_data}")
        print(f"DEBUG TOKEN DISPLAY: object.pk = {self.object.pk}")

        # Verify the token data matches the current object for security
        if token_data and token_data.get("credential_id") == self.object.pk:
            context["token_data"] = token_data
            context["show_token"] = True
            # Mark for removal after template renders
            context["clear_token_session"] = True
            print("DEBUG TOKEN DISPLAY: Token will be shown")
        else:
            context["show_token"] = False
            print(
                f"DEBUG TOKEN DISPLAY: Token will NOT be shown. Reason: token_data={token_data}, credential_id_match={token_data.get('credential_id') if token_data else None} == {self.object.pk}"
            )
            messages.warning(
                self.request,
                "Token display session expired. For security, tokens are only shown once.",
            )

        return context

    def render_to_response(self, context, **response_kwargs):
        """Override to clear token session after rendering."""
        response = super().render_to_response(context, **response_kwargs)

        # Clear the token from session after successful render
        if context.get("clear_token_session"):
            self.request.session.pop("credential_token", None)

        return response


class DeviceCredentialSetTokenModalView(LoginRequiredMixin, DetailView):
    """HTMX view for displaying token reveal modal."""

    model = DeviceCredentialSet
    template_name = "netbox_toolkit_plugin/htmx/token_modal.html"
    context_object_name = "credential_set"

    def get_queryset(self):
        # Users can only view their own credential sets
        return DeviceCredentialSet.objects.filter(owner=self.request.user)
