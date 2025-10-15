from dcim.api.serializers import DeviceSerializer, PlatformSerializer
from netbox.api.serializers import NetBoxModelSerializer, WritableNestedSerializer

from rest_framework import serializers

from ..models import Command, CommandLog, CommandVariable, DeviceCredentialSet


class CommandVariableSerializer(NetBoxModelSerializer):
    """Serializer for CommandVariable model following NetBox patterns"""

    class Meta:
        model = CommandVariable
        fields = (
            "id",
            "name",
            "display_name",
            "variable_type",
            "required",
            "help_text",
            "default_value",
        )


class CommandExecutionSerializer(serializers.Serializer):
    """Serializer for command execution input validation using credential tokens"""

    device_id = serializers.IntegerField(
        help_text="ID of the device to execute the command on"
    )
    credential_token = serializers.CharField(
        max_length=128, help_text="Credential token for stored device credentials"
    )
    variables = serializers.DictField(
        child=serializers.CharField(max_length=500),
        required=False,
        default=dict,
        help_text="Variable values for command substitution (key-value pairs)",
    )
    timeout = serializers.IntegerField(
        required=False,
        default=30,
        min_value=5,
        max_value=300,
        help_text="Command execution timeout in seconds (5-300)",
    )

    def validate_device_id(self, value):
        """Validate that the device exists and has required attributes"""
        from dcim.models import Device

        try:
            device = Device.objects.get(id=value)
            if not device.platform:
                raise serializers.ValidationError(
                    "Device must have a platform assigned for command execution"
                )
            if not device.primary_ip:
                raise serializers.ValidationError(
                    "Device must have a primary IP address for command execution"
                )
            return value
        except Device.DoesNotExist as e:
            raise serializers.ValidationError("Device not found") from e

    def validate_credential_token(self, value):
        """Validate that the credential token exists and belongs to the requesting user"""
        try:
            # Get the current user from context
            request = self.context.get("request")
            if not request or not request.user:
                raise serializers.ValidationError("Authentication required")

            from netbox_toolkit_plugin.models import DeviceCredentialSet

            DeviceCredentialSet.objects.get(access_token=value, owner=request.user)
            return value
        except DeviceCredentialSet.DoesNotExist as e:
            raise serializers.ValidationError(
                "Invalid credential token or token does not belong to current user"
            ) from e

    def validate(self, data):
        """Cross-field validation and object retrieval"""
        from dcim.models import Device

        from netbox_toolkit_plugin.models import DeviceCredentialSet

        # Get the actual objects for use in views
        device = Device.objects.get(id=data["device_id"])
        request = self.context.get("request")
        credential_set = DeviceCredentialSet.objects.get(
            access_token=data["credential_token"], owner=request.user
        )

        # Verify credential set supports device platform (if platform restrictions exist)
        if (
            credential_set.platforms.exists()
            and device.platform not in credential_set.platforms.all()
        ):
            raise serializers.ValidationError(
                f"Credential set '{credential_set.name}' does not support "
                f"platform '{device.platform.name}'"
            )

        data["device"] = device
        data["credential_set"] = credential_set
        return data


class NestedCommandSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:netbox_toolkit_plugin-api:command-detail"
    )

    class Meta:
        model = Command
        fields = ("id", "url", "name", "display")


class CommandSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:netbox_toolkit_plugin-api:command-detail"
    )
    platforms = PlatformSerializer(nested=True, many=True)
    variables = CommandVariableSerializer(many=True, read_only=True)

    class Meta:
        model = Command
        fields = (
            "id",
            "url",
            "display",
            "name",
            "command",
            "description",
            "platforms",
            "command_type",
            "variables",
            "tags",
            "custom_fields",
            "created",
            "last_updated",
        )
        brief_fields = ("id", "url", "display", "name", "command_type", "platforms")


class CommandLogSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:netbox_toolkit_plugin-api:commandlog-detail"
    )
    command = NestedCommandSerializer()
    device = DeviceSerializer(nested=True)

    class Meta:
        model = CommandLog
        fields = (
            "id",
            "url",
            "display",
            "command",
            "device",
            "output",
            "username",
            "execution_time",
            "success",
            "error_message",
            "execution_duration",
            "created",
            "last_updated",
        )
        brief_fields = (
            "id",
            "url",
            "display",
            "command",
            "device",
            "username",
            "execution_time",
            "success",
        )


class DeviceCredentialSetSerializer(NetBoxModelSerializer):
    """Minimal serializer for DeviceCredentialSet - used only by NetBox's event system"""

    class Meta:
        model = DeviceCredentialSet
        fields = (
            "id",
            "name",
            "description",
            "created_at",
            "last_used",
            "is_active",
            "tags",
            "custom_fields",
            "created",
            "last_updated",
        )


class BulkCommandExecutionSerializer(serializers.Serializer):
    """Serializer for bulk command execution validation using credential tokens"""

    command_id = serializers.IntegerField(help_text="ID of the command to execute")
    device_id = serializers.IntegerField(
        help_text="ID of the device to execute the command on"
    )
    credential_token = serializers.CharField(
        max_length=128, help_text="Credential token for stored device credentials"
    )
    variables = serializers.DictField(
        child=serializers.CharField(max_length=500),
        required=False,
        default=dict,
        help_text="Variable values for command substitution (key-value pairs)",
    )
    timeout = serializers.IntegerField(
        required=False,
        default=30,
        min_value=5,
        max_value=300,
        help_text="Command execution timeout in seconds",
    )

    def validate_command_id(self, value):
        """Validate that the command exists"""
        try:
            Command.objects.get(id=value)
            return value
        except Command.DoesNotExist as e:
            raise serializers.ValidationError("Command not found") from e

    def validate_device_id(self, value):
        """Validate that the device exists"""
        from dcim.models import Device

        try:
            device = Device.objects.get(id=value)
            if not device.platform:
                raise serializers.ValidationError(
                    "Device must have a platform assigned"
                )
            return value
        except Device.DoesNotExist as e:
            raise serializers.ValidationError("Device not found") from e

    def validate_credential_token(self, value):
        """Validate that the credential token exists and belongs to the requesting user"""
        try:
            # Get the current user from context
            request = self.context.get("request")
            if not request or not request.user:
                raise serializers.ValidationError("Authentication required")

            from netbox_toolkit_plugin.models import DeviceCredentialSet

            DeviceCredentialSet.objects.get(access_token=value, owner=request.user)
            return value
        except DeviceCredentialSet.DoesNotExist as e:
            raise serializers.ValidationError(
                "Invalid credential token or token does not belong to current user"
            ) from e
