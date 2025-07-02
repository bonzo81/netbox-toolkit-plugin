"""Factory for creating device connectors."""
import logging
from typing import Type, Optional

from django.db.models import Model
from dcim.models import Device

from ..exceptions import UnsupportedPlatformError, DeviceConnectionError
from ..config import ToolkitConfig
from ..utils.logging import get_toolkit_logger
from .base import BaseDeviceConnector, ConnectionConfig
from .scrapli_connector import ScrapliConnector
from .netmiko_connector import NetmikoConnector

logger = get_toolkit_logger(__name__)


class ConnectorFactory:
    """Factory for creating device connectors with Scrapli primary and Netmiko fallback."""
    
    # Primary connector (high-performance)
    PRIMARY_CONNECTOR = ScrapliConnector
    
    # Fallback connector (legacy device support)
    FALLBACK_CONNECTOR = NetmikoConnector
    
    # Platform-specific connector mappings
    CONNECTOR_MAP = {
        # Scrapli-optimized platforms (use primary connector)
        'cisco_ios': ScrapliConnector,
        'cisco_nxos': ScrapliConnector,
        'cisco_iosxr': ScrapliConnector,
        'cisco_xe': ScrapliConnector,
        'ios': ScrapliConnector,
        'nxos': ScrapliConnector,
        'iosxr': ScrapliConnector,
        'ios-xe': ScrapliConnector,
        'ios-xr': ScrapliConnector,
        
        # Platforms that may work better with Netmiko fallback
        'juniper_junos': ScrapliConnector,  # Try Scrapli first
        'arista_eos': ScrapliConnector,     # Try Scrapli first  
        'linux': ScrapliConnector,          # Try Scrapli first
        
        # Legacy/specialized platforms - direct to Netmiko
        'hp_procurve': NetmikoConnector,
        'hp_comware': NetmikoConnector,
        'dell_os10': NetmikoConnector,
        'dell_powerconnect': NetmikoConnector,
        'cisco_asa': NetmikoConnector,
        'paloalto_panos': NetmikoConnector,
        'fortinet': NetmikoConnector,
        'mikrotik_routeros': NetmikoConnector,
        'ubiquiti_edge': NetmikoConnector,
    }
    
    @classmethod
    def create_connector(
        cls,
        device: Device,
        username: str,
        password: str,
        connector_type: Optional[str] = None,
        use_fallback: bool = True
    ) -> BaseDeviceConnector:
        """
        Create a device connector with Scrapli primary and Netmiko fallback strategy.
        
        Args:
            device: NetBox Device instance
            username: Authentication username
            password: Authentication password
            connector_type: Override connector type (optional)
            use_fallback: Whether to attempt fallback to Netmiko on Scrapli failure
            
        Returns:
            Device connector instance
            
        Raises:
            UnsupportedPlatformError: If platform is not supported by any connector
            DeviceConnectionError: If both primary and fallback connectors fail
        """
        logger.debug("Creating connector for device %s (platform: %s)", 
                    device.name, device.platform)
        
        config = cls._build_connection_config(device, username, password)
        
        # Determine connector class
        if connector_type:
            logger.debug("Using override connector type: %s", connector_type)
            connector_class = cls._get_connector_by_type(connector_type)
            logger.info("Created %s connector for device %s", 
                       connector_class.__name__, device.name)
            return connector_class(config)
        
        # Try platform-specific connector first
        primary_connector_class = cls._get_primary_connector_by_platform(config.platform)
        
        try:
            logger.debug("Attempting primary connector: %s", primary_connector_class.__name__)
            
            # Create a clean config for the primary connector
            primary_config = cls._prepare_connector_config(config, primary_connector_class)
            connector = primary_connector_class(primary_config)
            
            # For ScrapliConnector, rely on fast-fail logic in connect() method
            # instead of pre-testing connection. This avoids double connection attempts.
            logger.info("Created %s connector for device %s", 
                       primary_connector_class.__name__, device.name)
            return connector
            
        except Exception as e:
            # Check if this is a fast-fail scenario for immediate Netmiko fallback
            error_msg = str(e)
            if (use_fallback and 
                primary_connector_class == ScrapliConnector and 
                ("Fast-fail to Netmiko" in error_msg or 
                 ToolkitConfig.should_fast_fail_to_netmiko(error_msg))):
                logger.info("Fast-fail pattern detected during connector creation for %s", device.name)
                return cls._create_fallback_connector(config, device.name, error_msg)
            elif use_fallback and primary_connector_class != NetmikoConnector:
                logger.warning("Primary connector failed for %s: %s", device.name, error_msg)
                return cls._create_fallback_connector(config, device.name, error_msg)
            else:
                raise DeviceConnectionError(f"Connector creation failed: {error_msg}")
    
    @classmethod
    def _create_fallback_connector(cls, config: ConnectionConfig, device_name: str, primary_error: str) -> BaseDeviceConnector:
        """Create fallback Netmiko connector when primary fails."""
        logger.info("Falling back to Netmiko connector for device %s", device_name)
        try:
            # Create a clean config specifically for Netmiko
            fallback_config = cls._prepare_connector_config(config, NetmikoConnector)
            connector = NetmikoConnector(fallback_config)
            logger.info("Successfully created Netmiko fallback connector for device %s", device_name)
            return connector
        except Exception as fallback_error:
            logger.error("Both primary and fallback connectors failed for %s", device_name)
            raise DeviceConnectionError(
                f"Both connectors failed. Primary error: {primary_error}. "
                f"Fallback error: {str(fallback_error)}"
            )
    
    @classmethod
    def _prepare_connector_config(cls, base_config: ConnectionConfig, connector_class: Type[BaseDeviceConnector]) -> ConnectionConfig:
        """Prepare a clean configuration for a specific connector type."""
        # Create a copy of the base config
        config = ConnectionConfig(
            hostname=base_config.hostname,
            username=base_config.username,
            password=base_config.password,
            port=base_config.port,
            timeout_socket=base_config.timeout_socket,
            timeout_transport=base_config.timeout_transport,
            timeout_ops=base_config.timeout_ops,
            auth_strict_key=base_config.auth_strict_key,
            transport=base_config.transport,
            platform=base_config.platform,
            extra_options=None  # Start with clean extra_options
        )
        
        # Add connector-specific configurations
        if connector_class == NetmikoConnector:
            # For Netmiko, add Netmiko-specific config to extra_options
            netmiko_config = ToolkitConfig.get_netmiko_config()
            config.extra_options = netmiko_config.copy()
            logger.debug("Prepared Netmiko config with options: %s", list(netmiko_config.keys()))
        
        elif connector_class == ScrapliConnector:
            # For Scrapli, keep extra_options clean (transport options are handled separately)
            # Any Scrapli-specific config would go here
            config.extra_options = None
            logger.debug("Prepared clean Scrapli config")
        
        return config
    
    @classmethod
    def _build_connection_config(cls, device: Device, username: str, password: str) -> ConnectionConfig:
        """Build connection configuration from device properties."""
        logger.debug("Building connection config for device %s", device.name)
        
        # Get device connection details
        hostname = str(device.primary_ip.address.ip) if device.primary_ip else device.name
        platform = str(device.platform).lower() if device.platform else None
        
        logger.debug("Connection details - hostname: %s, platform: %s", hostname, platform)
        
        # Normalize platform using config
        normalized_platform = ToolkitConfig.normalize_platform(platform)
        logger.debug("Normalized platform: %s -> %s", platform, normalized_platform)
        
        # Get timeouts based on device type
        device_model = str(device.device_type.model) if device.device_type else None
        timeouts = ToolkitConfig.get_timeouts_for_device(device_model)
        
        # Build configuration
        config = ConnectionConfig(
            hostname=hostname,
            username=username,
            password=password,
            platform=normalized_platform,
            timeout_socket=timeouts['socket'],
            timeout_transport=timeouts['transport'],
            timeout_ops=timeouts['ops'],
        )
        
        # Add device-specific customizations if needed
        config = cls._customize_config_for_device(config, device)
        
        return config
    
    @classmethod
    def _customize_config_for_device(cls, config: ConnectionConfig, device: Device) -> ConnectionConfig:
        """Customize configuration based on device properties."""
        # Add custom port if specified in device custom fields
        # (This would require custom fields to be defined in NetBox)
        # if hasattr(device, 'cf') and device.cf.get('ssh_port'):
        #     config.port = int(device.cf['ssh_port'])
        
        return config
    
    @classmethod
    def _get_connector_by_type(cls, connector_type: str) -> Type[BaseDeviceConnector]:
        """Get connector class by explicit type."""
        connector_type_lower = connector_type.lower()
        if connector_type_lower == 'scrapli':
            return ScrapliConnector
        elif connector_type_lower == 'netmiko':
            return NetmikoConnector
        else:
            raise UnsupportedPlatformError(f"Unsupported connector type: {connector_type}")
    
    @classmethod
    def _get_primary_connector_by_platform(cls, platform: Optional[str]) -> Type[BaseDeviceConnector]:
        """Get primary connector class by device platform."""
        if not platform:
            return cls.PRIMARY_CONNECTOR
        
        platform_lower = platform.lower()
        
        # Check for exact match first
        if platform_lower in cls.CONNECTOR_MAP:
            return cls.CONNECTOR_MAP[platform_lower]
        
        # Check for partial matches (e.g., 'ios' in 'cisco_ios')
        for supported_platform, connector_class in cls.CONNECTOR_MAP.items():
            if platform_lower in supported_platform or supported_platform in platform_lower:
                return connector_class
        
        # If no specific match, use primary connector
        return cls.PRIMARY_CONNECTOR
    
    @classmethod
    def _get_connector_by_platform(cls, platform: Optional[str]) -> Type[BaseDeviceConnector]:
        """Legacy method for backward compatibility."""
        return cls._get_primary_connector_by_platform(platform)
    
    @classmethod
    def get_supported_platforms(cls) -> list[str]:
        """Get list of supported platforms from both connectors."""
        scrapli_platforms = ScrapliConnector.get_supported_platforms()
        netmiko_platforms = NetmikoConnector.get_supported_platforms()
        
        # Combine and deduplicate
        all_platforms = list(set(scrapli_platforms + netmiko_platforms + list(cls.CONNECTOR_MAP.keys())))
        return sorted(all_platforms)
    
    @classmethod
    def is_platform_supported(cls, platform: str) -> bool:
        """Check if a platform is supported by any connector."""
        if not platform:
            return True  # Default connectors can handle unknown platforms
        
        platform_lower = platform.lower()
        
        # Check exact match in our mapping
        if platform_lower in cls.CONNECTOR_MAP:
            return True
        
        # Check partial matches
        for supported_platform in cls.CONNECTOR_MAP.keys():
            if platform_lower in supported_platform or supported_platform in platform_lower:
                return True
        
        # Check if either connector supports it
        if (platform_lower in [p.lower() for p in ScrapliConnector.get_supported_platforms()] or
            platform_lower in [p.lower() for p in NetmikoConnector.get_supported_platforms()]):
            return True
        
        return False
    
    @classmethod
    def get_recommended_connector(cls, platform: Optional[str]) -> str:
        """Get recommended connector type for a platform."""
        connector_class = cls._get_primary_connector_by_platform(platform)
        if connector_class == ScrapliConnector:
            return "scrapli"
        elif connector_class == NetmikoConnector:
            return "netmiko"
        else:
            return "scrapli"  # Default recommendation
