"""Service for device-related operations."""
from typing import List, Optional

from dcim.models import Device

from ..models import Command


class DeviceService:
    """Service for device-related operations."""
    
    @staticmethod
    def get_available_commands(device: Device) -> List[Command]:
        """
        Get all commands available for a device based on its platform.
        
        Args:
            device: The device to get commands for
            
        Returns:
            List of available commands
        """
        if not device.platform:
            return []
        
        commands = Command.objects.filter(platform=device.platform)
        
        return list(commands)
    
    @staticmethod
    def get_device_connection_info(device: Device) -> dict:
        """
        Get connection information for a device.
        
        Args:
            device: The device to get connection info for
            
        Returns:
            Dictionary with connection information
        """
        hostname = str(device.primary_ip.address.ip) if device.primary_ip else device.name
        platform = str(device.platform).lower() if device.platform else None
        
        info = {
            'hostname': hostname,
            'platform': platform,
            'has_primary_ip': device.primary_ip is not None,
        }
        
        return info
    
    @staticmethod
    def validate_device_for_commands(device: Device) -> tuple[bool, Optional[str], dict]:
        """
        Validate if a device is ready for command execution.
        
        Args:
            device: The device to validate
            
        Returns:
            Tuple of (is_valid, error_message, validation_checks)
            validation_checks is a dict with check names as keys and booleans as values
        """
        # Initialize validation checks
        validation_checks = {
            'has_platform': device.platform is not None,
            'has_primary_ip': device.primary_ip is not None,
            'has_hostname': bool(device.name),  # Check if device has a name
            'platform_supported': False,        # Will be set below if platform exists
        }
        
        # Additional logic for more complex checks
        if validation_checks['has_platform']:
            validation_checks['platform_supported'] = True  # If platform exists, we consider it supported
        
        # Determine overall validity and error message
        is_valid = True
        error_message = None
        
        if not validation_checks['has_platform']:
            is_valid = False
            error_message = "Device has no platform assigned"
        elif not validation_checks['has_primary_ip'] and not validation_checks['has_hostname']:
            is_valid = False
            error_message = "Device has no primary IP address or hostname"
        
        return is_valid, error_message, validation_checks
