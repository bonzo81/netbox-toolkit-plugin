"""
API ViewSet for DeviceCredentialSet resources
"""

from django.http import Http404

from netbox.api.viewsets import NetBoxModelViewSet

from drf_spectacular.utils import OpenApiResponse, extend_schema, extend_schema_view
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from ... import filtersets, models
from ..mixins import APIResponseMixin, PermissionCheckMixin
from ..serializers import DeviceCredentialSetSerializer


@extend_schema_view(
    list=extend_schema(
        summary="List device credential sets",
        description="Retrieve a list of device credential sets owned by the current user. "
        "Credentials are never exposed via the API for security.",
        responses={200: DeviceCredentialSetSerializer(many=True)},
    ),
    retrieve=extend_schema(
        summary="Retrieve a device credential set",
        description="Retrieve details of a specific device credential set owned by the current user. "
        "Credentials are never exposed via the API for security.",
        responses={200: DeviceCredentialSetSerializer()},
    ),
    create=extend_schema(
        summary="Create credential set (Not Allowed)",
        description="Credential sets can only be created via the web interface for security reasons. "
        "This prevents credentials from being transmitted over API calls.",
        responses={405: OpenApiResponse(description="Method not allowed")},
    ),
    update=extend_schema(
        summary="Update credential set (Not Allowed)",
        description="Credential sets can only be modified via the web interface for security reasons. "
        "This prevents credentials from being transmitted over API calls.",
        responses={405: OpenApiResponse(description="Method not allowed")},
    ),
    partial_update=extend_schema(
        summary="Partially update credential set (Not Allowed)",
        description="Credential sets can only be modified via the web interface for security reasons. "
        "This prevents credentials from being transmitted over API calls.",
        responses={405: OpenApiResponse(description="Method not allowed")},
    ),
    destroy=extend_schema(
        summary="Delete a device credential set",
        description="Delete a device credential set owned by the current user. "
        "This will invalidate the credential token and remove all stored credentials.",
        responses={
            204: OpenApiResponse(description="Credential set deleted successfully")
        },
    ),
)
class DeviceCredentialSetViewSet(
    NetBoxModelViewSet, APIResponseMixin, PermissionCheckMixin
):
    serializer_class = DeviceCredentialSetSerializer
    filterset_class = filtersets.DeviceCredentialSetFilterSet

    def get_queryset(self):
        """Return only credential sets owned by the current user"""
        if not self.request.user.is_authenticated:
            return models.DeviceCredentialSet.objects.none()

        return models.DeviceCredentialSet.objects.filter(
            owner=self.request.user
        ).prefetch_related("platforms", "tags")

    def create(self, request, *args, **kwargs):
        """Prevent API creation of credential sets for security"""
        return Response(
            {
                "error": "Credential sets can only be created via the web interface for security reasons. "
                "This prevents credentials from being transmitted over API calls.",
                "detail": "Use the NetBox web interface to create credential sets with secure form handling.",
            },
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )

    def update(self, request, *args, **kwargs):
        """Prevent API updates of credential sets for security"""
        return Response(
            {
                "error": "Credential sets can only be modified via the web interface for security reasons. "
                "This prevents credentials from being transmitted over API calls.",
                "detail": "Use the NetBox web interface to modify credential sets with secure form handling.",
            },
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )

    def partial_update(self, request, *args, **kwargs):
        """Prevent API partial updates of credential sets for security"""
        return Response(
            {
                "error": "Credential sets can only be modified via the web interface for security reasons. "
                "This prevents credentials from being transmitted over API calls.",
                "detail": "Use the NetBox web interface to modify credential sets with secure form handling.",
            },
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )

    @extend_schema(
        summary="Regenerate credential token",
        description="Regenerate the credential token for a device credential set. "
        "This will invalidate the previous token and return the new one. "
        "Only the credential set owner can regenerate tokens.",
        responses={
            200: OpenApiResponse(
                description="Token regenerated successfully",
                examples={
                    "application/json": {
                        "message": "Credential token regenerated successfully",
                        "access_token": "new-token-value-here",
                        "credential_set_id": 1,
                        "credential_set_name": "My Cisco Credentials",
                    }
                },
            ),
            404: OpenApiResponse(description="Credential set not found"),
            403: OpenApiResponse(description="Permission denied"),
        },
    )
    @action(detail=True, methods=["post"])
    def regenerate_token(self, request, pk=None):
        """Regenerate credential token for a credential set"""
        try:
            credential_set = self.get_object()

            from ...services.credential_service import CredentialService

            credential_service = CredentialService()

            success, new_token, error = credential_service.regenerate_token(
                credential_set.id, request.user
            )

            if not success:
                return Response({"error": error}, status=status.HTTP_400_BAD_REQUEST)

            return Response({
                "message": "Credential token regenerated successfully",
                "access_token": new_token,
                "credential_set_id": credential_set.id,
                "credential_set_name": credential_set.name,
            })

        except Http404:
            return Response(
                {"error": "Credential set not found"}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": "Failed to regenerate token", "detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @extend_schema(
        summary="Test credential set connectivity",
        description="Test connectivity to a device using stored credentials from this credential set. "
        "This validates that the credentials work without exposing them.",
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "device_id": {
                        "type": "integer",
                        "description": "ID of the device to test connectivity to",
                    }
                },
                "required": ["device_id"],
            }
        },
        responses={
            200: OpenApiResponse(
                description="Connectivity test successful",
                examples={
                    "application/json": {
                        "message": "Connectivity test successful",
                        "device_name": "Router01",
                        "device_ip": "192.168.1.1",
                        "platform": "cisco_ios",
                        "test_result": "Connection established successfully",
                    }
                },
            ),
            400: OpenApiResponse(description="Invalid device or connectivity failed"),
            404: OpenApiResponse(description="Credential set or device not found"),
        },
    )
    @action(detail=True, methods=["post"])
    def test_connectivity(self, request, pk=None):
        """Test connectivity using stored credentials"""
        try:
            credential_set = self.get_object()
            device_id = request.data.get("device_id")

            if not device_id:
                return Response(
                    {"error": "device_id is required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Import here to avoid circular imports
            from dcim.models import Device

            try:
                device = Device.objects.get(id=device_id)
            except Device.DoesNotExist:
                return Response(
                    {"error": "Device not found"}, status=status.HTTP_404_NOT_FOUND
                )

            from ...services.credential_service import CredentialService

            credential_service = CredentialService()

            # Test connectivity using the service
            success, result, error = credential_service.test_credentials_connectivity(
                credential_set.access_token, request.user, device, timeout=10
            )

            if success:
                return Response({
                    "message": "Connectivity test successful",
                    "device_name": device.name,
                    "device_ip": str(device.primary_ip.address.ip),
                    "platform": device.platform.name,
                    "test_result": result.get(
                        "message", "Connection established successfully"
                    ),
                })
            else:
                return Response(
                    {
                        "error": "Connectivity test failed",
                        "device_name": device.name,
                        "device_ip": str(device.primary_ip.address.ip),
                        "test_result": error,
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

        except Http404:
            return Response(
                {"error": "Credential set not found"}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": "Test connectivity failed", "detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
