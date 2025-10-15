"""Command-related views for the NetBox Toolkit Plugin."""

from django.shortcuts import redirect, render
from django.urls import reverse

from netbox.views.generic import (
    ObjectChangeLogView,
    ObjectDeleteView,
    ObjectEditView,
    ObjectListView,
    ObjectView,
)

from ..forms import CommandForm, CommandVariableFormSet
from ..models import Command


class CommandListView(ObjectListView):
    queryset = Command.objects.all()
    filterset = None  # Will update this after import
    table = None  # Will update this after import
    template_name = "netbox_toolkit_plugin/command_list.html"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from ..filtersets import CommandFilterSet
        from ..tables import CommandTable

        self.filterset = CommandFilterSet
        self.table = CommandTable


class CommandEditView(ObjectEditView):
    queryset = Command.objects.all()
    form = CommandForm
    template_name = "netbox_toolkit_plugin/command_edit.html"

    def get_success_url(self):
        """Override to use correct plugin namespace"""
        if self.object and self.object.pk:
            return reverse(
                "plugins:netbox_toolkit_plugin:command_detail",
                kwargs={"pk": self.object.pk},
            )
        return reverse("plugins:netbox_toolkit_plugin:command_list")

    def get_return_url(self, request, instance):
        """Override to use correct plugin namespace for cancel/return links"""
        # Check if there's a return URL in the request
        return_url = request.GET.get("return_url")
        if return_url:
            return return_url
        # Return proper reverse URL
        return reverse("plugins:netbox_toolkit_plugin:command_list")

    def get_extra_context(self, request, instance):
        """Override to provide additional context with correct URLs"""
        context = super().get_extra_context(request, instance)

        # Override any auto-generated URLs that might be using wrong namespace
        context["base_template"] = "generic/object_edit.html"
        context["return_url"] = self.get_return_url(request, instance)

        return context

    def get(self, request, *args, **kwargs):
        """Override GET to add formset to form"""
        obj = self.get_object(**kwargs)
        obj = self.alter_object(obj, request, args, kwargs)

        # Create the main form
        form = self.form(instance=obj)

        # Add formset to the form
        form.variable_formset = CommandVariableFormSet(instance=obj, prefix="variables")

        return render(
            request,
            self.template_name,
            {
                "object": obj,
                "form": form,
                **self.get_extra_context(request, obj),
            },
        )

    def post(self, request, *args, **kwargs):
        """Override POST to handle formset processing"""
        obj = self.get_object(**kwargs)

        # Set self.object so get_success_url can access it
        self.object = obj

        # Create the main form with POST data
        form = self.form(data=request.POST, files=request.FILES, instance=obj)

        # Create formset with POST data
        form.variable_formset = CommandVariableFormSet(
            request.POST, instance=obj, prefix="variables"
        )

        if form.is_valid() and form.variable_formset.is_valid():
            # Save the main form
            self.object = form.save()

            # Save the formset
            form.variable_formset.instance = self.object
            form.variable_formset.save()

            return redirect(self.get_success_url())
        else:
            # Form or formset validation failed - redisplay with errors
            return render(
                request,
                self.template_name,
                {
                    "object": obj,
                    "form": form,
                    **self.get_extra_context(request, obj),
                },
            )


class CommandVariableFormView(ObjectView):
    """
    HTMX view to return a new variable form for dynamic addition
    """

    queryset = Command.objects.all()

    def get(self, request, pk):
        """Return rendered HTML for a new variable form"""
        # For new commands (pk=0), create an empty Command instance
        if pk == 0:
            command = Command()
        else:
            try:
                command = self.get_object(pk=pk)
            except Command.DoesNotExist:
                command = Command()

        # Create a formset to get the empty form
        formset = CommandVariableFormSet(instance=command, prefix="variables")

        # Get the total forms count from the request to set proper form index
        total_forms = int(request.GET.get("total_forms", 0))

        # Create a form with the proper index
        empty_form = formset.empty_form

        context = {
            "form": empty_form,
            "form_index": total_forms,
        }

        return render(request, "netbox_toolkit_plugin/htmx/variable_form.html", context)


class CommandView(ObjectView):
    queryset = Command.objects.all()
    template_name = "netbox_toolkit_plugin/command.html"

    def get_extra_context(self, request, instance):
        """Add permission context to the template"""
        context = super().get_extra_context(request, instance)

        # Add permission information for the template using NetBox's object-based permissions
        context["can_execute"] = False
        if instance.command_type == "show":
            context["can_execute"] = self._user_has_action_permission(
                request.user, instance, "execute_show"
            )
        elif instance.command_type == "config":
            context["can_execute"] = self._user_has_action_permission(
                request.user, instance, "execute_config"
            )

        # NetBox will automatically handle 'change' and 'delete' permissions through standard actions
        context["can_edit"] = self._user_has_action_permission(
            request.user, instance, "change"
        )
        context["can_delete"] = self._user_has_action_permission(
            request.user, instance, "delete"
        )

        return context

    def _user_has_action_permission(self, user, obj, action):
        """Check if user has permission for a specific action on an object using NetBox's ObjectPermission system"""
        from django.contrib.contenttypes.models import ContentType

        from users.models import ObjectPermission

        # Get content type for the object
        content_type = ContentType.objects.get_for_model(obj)

        # Check if user has any ObjectPermissions with the required action
        user_permissions = ObjectPermission.objects.filter(
            object_types__in=[content_type], actions__contains=[action], enabled=True
        )

        # Check if user is assigned to any groups with this permission
        user_groups = user.groups.all()
        for permission in user_permissions:
            # Check if permission applies to user or user's groups
            if (
                permission.users.filter(id=user.id).exists()
                or permission.groups.filter(
                    id__in=user_groups.values_list("id", flat=True)
                ).exists()
            ):
                # If there are constraints, evaluate them
                if permission.constraints:
                    # Create a queryset with the constraints and check if the object matches
                    queryset = content_type.model_class().objects.filter(
                        **permission.constraints
                    )
                    if queryset.filter(id=obj.id).exists():
                        return True
                else:
                    # No constraints means permission applies to all objects of this type
                    return True

        return False


class CommandDeleteView(ObjectDeleteView):
    queryset = Command.objects.all()

    def get_success_url(self):
        """Override to use correct plugin namespace"""

        return reverse("plugins:netbox_toolkit_plugin:command_list")


class CommandChangeLogView(ObjectChangeLogView):
    queryset = Command.objects.all()
