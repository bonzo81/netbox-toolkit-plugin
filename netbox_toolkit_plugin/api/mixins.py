"""
Common mixins and utilities for NetBox Toolkit API views
"""
from rest_framework.response import Response
from django.contrib.contenttypes.models import ContentType
from users.models import ObjectPermission


class APIResponseMixin:
    """Mixin to add consistent API response headers"""
    
    def finalize_response(self, request, response, *args, **kwargs):
        """Add custom headers to all responses"""
        response = super().finalize_response(request, response, *args, **kwargs)
        
        # Add API version header
        response['X-NetBox-Toolkit-API-Version'] = '1.0'
        
        return response


class PermissionCheckMixin:
    """Mixin for NetBox ObjectPermission checking"""
    
    def _user_has_action_permission(self, user, obj, action):
        """Check if user has permission for a specific action on an object using NetBox's ObjectPermission system"""
        # Get content type for the object
        content_type = ContentType.objects.get_for_model(obj)
        
        # Check if user has any ObjectPermissions with the required action
        user_permissions = ObjectPermission.objects.filter(
            object_types__in=[content_type],
            actions__contains=[action],
            enabled=True
        )
        
        # Check if user is assigned to any groups with this permission
        user_groups = user.groups.all()
        for permission in user_permissions:
            # Check if permission applies to user or user's groups
            if (permission.users.filter(id=user.id).exists() or 
                permission.groups.filter(id__in=user_groups.values_list('id', flat=True)).exists()):
                
                # If there are constraints, evaluate them
                if permission.constraints:
                    # Create a queryset with the constraints and check if the object matches
                    queryset = content_type.model_class().objects.filter(**permission.constraints)
                    if queryset.filter(id=obj.id).exists():
                        return True
                else:
                    # No constraints means permission applies to all objects of this type
                    return True
        
        return False
