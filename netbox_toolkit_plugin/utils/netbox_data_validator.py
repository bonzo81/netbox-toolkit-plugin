"""
NetBox Data Validation Utility

This module provides validation for NetBox data variables to ensure that
values provided via API actually exist on the target device.
"""

from dcim.models import Device


class NetBoxDataValidator:
    """Validator for NetBox data variables against device context"""

    @staticmethod
    def validate_interface(device: Device, interface_name: str) -> tuple[bool, str]:
        """
        Validate that an interface name exists on the specified device.

        Args:
            device: The NetBox Device object
            interface_name: The interface name to validate (e.g., "GigabitEthernet0/1")

        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            device.interfaces.get(name=interface_name)
            return True, ""
        except device.interfaces.model.DoesNotExist:
            available_interfaces = list(
                device.interfaces.values_list("name", flat=True)[:5]
            )
            if len(available_interfaces) < device.interfaces.count():
                available_interfaces.append("...")

            return False, (
                f"Interface '{interface_name}' not found on device '{device.name}'. "
                f"Available interfaces: {', '.join(available_interfaces)}"
            )

    @staticmethod
    def validate_vlan(device: Device, vlan_id: str) -> tuple[bool, str]:
        """
        Validate that a VLAN ID exists for the specified device.

        Args:
            device: The NetBox Device object
            vlan_id: The VLAN ID to validate (as string, e.g., "100")

        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            vlan_id_int = int(vlan_id)
        except ValueError:
            return False, f"VLAN ID '{vlan_id}' must be a valid integer"

        # First check device VLANs if available
        if hasattr(device, "vlans") and device.vlans.filter(vid=vlan_id_int).exists():
            return True, ""

        # Fallback to site VLANs
        if device.site:
            from ipam.models import VLAN

            if VLAN.objects.filter(site=device.site, vid=vlan_id_int).exists():
                return True, ""

        return False, (
            f"VLAN {vlan_id} not found for device '{device.name}' or its site"
        )

    @staticmethod
    def validate_ip_address(device: Device, ip_address: str) -> tuple[bool, str]:
        """
        Validate that an IP address is associated with the specified device.

        Args:
            device: The NetBox Device object
            ip_address: The IP address to validate (e.g., "192.168.1.1")

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check if IP is associated with any of the device's interfaces
        for interface in device.interfaces.all():
            if interface.ip_addresses.filter(address__net_contains=ip_address).exists():
                return True, ""

        # Check primary IP addresses
        if device.primary_ip4 and str(device.primary_ip4.address.ip) == ip_address:
            return True, ""
        if device.primary_ip6 and str(device.primary_ip6.address.ip) == ip_address:
            return True, ""

        return False, (
            f"IP address '{ip_address}' is not associated with device '{device.name}'"
        )

    @classmethod
    def validate_variable_value(
        cls, device: Device, variable_type: str, variable_name: str, value: str
    ) -> tuple[bool, str]:
        """
        Validate a variable value against the device context based on variable type.

        Args:
            device: The NetBox Device object
            variable_type: Type of variable (text, netbox_interface, netbox_vlan, netbox_ip)
            variable_name: Name of the variable (for error messages)
            value: The value to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not value or variable_type == "text":
            # Text variables and empty values don't need NetBox validation
            return True, ""

        if variable_type == "netbox_interface":
            return cls.validate_interface(device, value)
        elif variable_type == "netbox_vlan":
            return cls.validate_vlan(device, value)
        elif variable_type == "netbox_ip":
            return cls.validate_ip_address(device, value)
        else:
            # Unknown variable type - assume valid
            return True, ""
