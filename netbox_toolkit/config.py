"""Configuration settings for the NetBox Toolkit plugin."""
from typing import Dict, Any
from django.conf import settings


class ToolkitConfig:
    """Configuration class for toolkit settings."""
    
    # Default connection timeouts
    DEFAULT_TIMEOUTS = {
        'socket': 15,
        'transport': 15,
        'ops': 30,
        'banner': 15,
        'auth': 15,
    }
    
    # Device-specific timeout overrides
    DEVICE_TIMEOUTS = {
        'catalyst': {
            'socket': 20,
            'transport': 20,
            'ops': 45,
        },
        'nexus': {
            'socket': 25,
            'transport': 25,
            'ops': 60,
        },
    }
    
    # SSH transport options
    SSH_TRANSPORT_OPTIONS = {
        'disabled_algorithms': {
            'kex': [],  # Don't disable any key exchange methods
        },
        'allowed_kex': [
            # Modern algorithms
            'diffie-hellman-group-exchange-sha256',
            'diffie-hellman-group16-sha512',
            'diffie-hellman-group18-sha512',
            'diffie-hellman-group14-sha256',
            # Legacy algorithms for older devices
            'diffie-hellman-group-exchange-sha1',
            'diffie-hellman-group14-sha1',
            'diffie-hellman-group1-sha1',
        ],
    }
    
    # Netmiko configuration for fallback connections
    NETMIKO_CONFIG = {
        'banner_timeout': 20,
        'auth_timeout': 20,
        'global_delay_factor': 1,
        'use_keys': False,           # Disable SSH key authentication
        'allow_agent': False,        # Disable SSH agent
        # Session logging (disabled by default)
        'session_log': None,
        # Connection options for legacy devices
        'fast_cli': False,           # Disable for older devices
        'session_log_record_writes': False,
        'session_log_file_mode': 'write',
    }
    
    # Retry configuration
    RETRY_CONFIG = {
        'max_retries': 2,
        'retry_delay': 1,  # Reduced from 3s to 1s for faster fallback
        'backoff_multiplier': 1.5,  # Reduced from 2 to 1.5 for faster progression
    }
    
    # Fast connection test timeouts (for initial Scrapli viability testing)
    FAST_TEST_TIMEOUTS = {
        'socket': 8,      # Reduced from 15s to 8s for faster detection
        'transport': 8,   # Reduced from 15s to 8s for faster detection
        'ops': 15,        # Keep ops timeout reasonable for actual commands
    }
    
    # Error patterns that should trigger immediate fallback to Netmiko
    SCRAPLI_FAST_FAIL_PATTERNS = [
        "No matching key exchange",
        "No matching cipher",
        "No matching MAC",
        "connection not opened",
        "Error reading SSH protocol banner",
        "Connection refused", 
        "Operation timed out",
        "SSH handshake failed",
        "Protocol version not supported",
        "Unable to connect to port 22",
        "Name or service not known",
        "Network is unreachable"
    ]
    
    # Platform mappings for better recognition
    PLATFORM_ALIASES = {
        'ios': 'cisco_ios',
        'iosxe': 'cisco_ios',
        'nxos': 'cisco_nxos',
        'iosxr': 'cisco_iosxr',
        'junos': 'juniper_junos',
        'eos': 'arista_eos',
    }
    
    @classmethod
    def get_fast_test_timeouts(cls) -> Dict[str, int]:
        """Get fast connection test timeouts for initial viability testing."""
        return cls.FAST_TEST_TIMEOUTS.copy()
    
    @classmethod
    def should_fast_fail_to_netmiko(cls, error_message: str) -> bool:
        """Check if error message indicates immediate fallback to Netmiko is needed."""
        error_lower = error_message.lower()
        return any(pattern.lower() in error_lower for pattern in cls.SCRAPLI_FAST_FAIL_PATTERNS)
    
    @classmethod
    def get_timeouts_for_device(cls, device_type_model: str = None) -> Dict[str, int]:
        """Get timeout configuration for a specific device type."""
        timeouts = cls.DEFAULT_TIMEOUTS.copy()
        
        if device_type_model:
            model_lower = device_type_model.lower()
            for device_keyword, custom_timeouts in cls.DEVICE_TIMEOUTS.items():
                if device_keyword in model_lower:
                    timeouts.update(custom_timeouts)
                    break
        
        return timeouts
    
    @classmethod
    def normalize_platform(cls, platform: str) -> str:
        """Normalize platform name using aliases."""
        if not platform:
            return None
        
        platform_lower = platform.lower()
        return cls.PLATFORM_ALIASES.get(platform_lower, platform_lower)
    
    @classmethod
    def get_ssh_options(cls) -> Dict[str, Any]:
        """Get SSH transport options."""
        return cls.SSH_TRANSPORT_OPTIONS.copy()
    
    @classmethod
    def get_retry_config(cls) -> Dict[str, int]:
        """Get retry configuration."""
        return cls.RETRY_CONFIG.copy()
    
    @classmethod
    def get_ssh_transport_options(cls) -> Dict[str, Any]:
        """Get SSH transport options for Scrapli."""
        user_config = getattr(settings, 'NETBOX_TOOLKIT', {})
        return {**cls.SSH_TRANSPORT_OPTIONS, **user_config.get('ssh_options', {})}
    
    @classmethod
    def get_netmiko_config(cls) -> Dict[str, Any]:
        """Get Netmiko configuration for fallback connections."""
        user_config = getattr(settings, 'NETBOX_TOOLKIT', {})
        return {**cls.NETMIKO_CONFIG, **user_config.get('netmiko', {})}
