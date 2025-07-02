from rest_framework import serializers
from netbox.api.serializers import NetBoxModelSerializer, WritableNestedSerializer
from dcim.api.serializers import PlatformSerializer, DeviceSerializer
from ..models import Command, CommandLog

class CommandExecutionSerializer(serializers.Serializer):
    """Serializer for command execution input validation"""
    device_id = serializers.IntegerField(
        help_text="ID of the device to execute the command on"
    )
    username = serializers.CharField(
        max_length=100,
        help_text="Username for device authentication",
        trim_whitespace=True
    )
    password = serializers.CharField(
        max_length=255,
        style={'input_type': 'password'},
        help_text="Password for device authentication",
        trim_whitespace=False
    )
    timeout = serializers.IntegerField(
        required=False,
        default=30,
        min_value=5,
        max_value=300,
        help_text="Command execution timeout in seconds (5-300)"
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
        except Device.DoesNotExist:
            raise serializers.ValidationError("Device not found")
    
    def validate(self, data):
        """Cross-field validation and object retrieval"""
        from dcim.models import Device
        
        # Get the actual device object for use in views
        device = Device.objects.get(id=data['device_id'])
        data['device'] = device
        
        return data
    
    def validate_username(self, value):
        """Validate username format"""
        if not value.strip():
            raise serializers.ValidationError("Username cannot be empty")
        if len(value.strip()) < 2:
            raise serializers.ValidationError("Username must be at least 2 characters")
        return value.strip()
    
    def validate_password(self, value):
        """Validate password"""
        if not value:
            raise serializers.ValidationError("Password cannot be empty")
        if len(value) < 3:
            raise serializers.ValidationError("Password must be at least 3 characters")
        return value

class NestedCommandSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='plugins-api:netbox_toolkit-api:command-detail'
    )

    class Meta:
        model = Command
        fields = ('id', 'url', 'name', 'display')

class CommandSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='plugins-api:netbox_toolkit-api:command-detail'
    )
    platform = PlatformSerializer(nested=True)

    class Meta:
        model = Command
        fields = (
            'id', 'url', 'display', 'name', 'command', 'description', 
            'platform', 'command_type',
            'tags', 'custom_fields', 'created', 'last_updated'
        )
        brief_fields = ('id', 'url', 'display', 'name', 'command_type', 'platform')

class CommandLogSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='plugins-api:netbox_toolkit-api:commandlog-detail'
    )
    command = NestedCommandSerializer()
    device = DeviceSerializer(nested=True)

    class Meta:
        model = CommandLog
        fields = (
            'id', 'url', 'display', 'command', 'device', 'output', 
            'username', 'execution_time', 'success', 'error_message', 'execution_duration',
            'parsed_data', 'parsing_success', 'parsing_template',
            'created', 'last_updated'
        )
        brief_fields = ('id', 'url', 'display', 'command', 'device', 'username', 'execution_time', 'success')

class BulkCommandExecutionSerializer(serializers.Serializer):
    """Serializer for bulk command execution validation"""
    command_id = serializers.IntegerField(
        help_text="ID of the command to execute"
    )
    device_id = serializers.IntegerField(
        help_text="ID of the device to execute the command on"
    )
    username = serializers.CharField(
        max_length=100,
        help_text="Username for device authentication"
    )
    password = serializers.CharField(
        max_length=255,
        style={'input_type': 'password'},
        help_text="Password for device authentication"
    )
    timeout = serializers.IntegerField(
        required=False,
        default=30,
        min_value=5,
        max_value=300,
        help_text="Command execution timeout in seconds"
    )
    
    def validate_command_id(self, value):
        """Validate that the command exists"""
        try:
            Command.objects.get(id=value)
            return value
        except Command.DoesNotExist:
            raise serializers.ValidationError("Command not found")
    
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
        except Device.DoesNotExist:
            raise serializers.ValidationError("Device not found")
