"""Configuration settings for the NetBox Toolkit plugin."""

from typing import Any

from django.conf import settings

# Plugin metadata - required by NetBox's plugin discovery system
__version__ = "0.1.1"
__author__ = "Andy Norwood"

# Make these available as module-level attributes for NetBox's plugin system
version = __version__
author = __author__
release_track = "stable"  # or "beta", "alpha" - indicates the release track


class ToolkitSettings:
    """Configuration class for toolkit settings."""

    # Default connection timeouts
    DEFAULT_TIMEOUTS = {
        "socket": 15,
        "transport": 15,
        "ops": 30,
        "banner": 15,
        "auth": 15,
    }

    # Device-specific timeout overrides
    DEVICE_TIMEOUTS = {
        "catalyst": {
            "socket": 20,
            "transport": 20,
            "ops": 45,
        },
        "nexus": {
            "socket": 25,
            "transport": 25,
            "ops": 60,
        },
    }

    # Security configuration for credential encryption
    DEFAULT_SECURITY_CONFIG = {
        "pepper": None,  # Must be set via environment variable or config
        "argon2": {
            "time_cost": 3,  # 3 iterations (good balance of security/performance)
            "memory_cost": 65536,  # 64 MB memory usage
            "parallelism": 1,  # 1 thread (adjust based on CPU cores)
            "hash_len": 32,  # 32 byte hash output
            "salt_len": 16,  # 16 byte salt length
        },
        "master_key_derivation": "argon2id",  # Use Argon2id instead of PBKDF2
    }

    # SSH transport options
    SSH_TRANSPORT_OPTIONS = {
        "disabled_algorithms": {
            "kex": [],  # Don't disable any key exchange methods
        },
        "allowed_kex": [
            # Modern algorithms
            "diffie-hellman-group-exchange-sha256",
            "diffie-hellman-group16-sha512",
            "diffie-hellman-group18-sha512",
            "diffie-hellman-group14-sha256",
            # Legacy algorithms for older devices
            "diffie-hellman-group-exchange-sha1",
            "diffie-hellman-group14-sha1",
            "diffie-hellman-group1-sha1",
        ],
    }

    # Netmiko configuration for fallback connections
    NETMIKO_CONFIG = {
        "banner_timeout": 20,
        "auth_timeout": 20,
        "global_delay_factor": 1,
        "use_keys": False,  # Disable SSH key authentication
        "allow_agent": False,  # Disable SSH agent
        # Session logging (disabled by default)
        "session_log": None,
        # Connection options for legacy devices
        "fast_cli": False,  # Disable for older devices
        "session_log_record_writes": False,
        "session_log_file_mode": "write",
    }

    # Retry configuration
    RETRY_CONFIG = {
        "max_retries": 2,
        "retry_delay": 1,  # Reduced from 3s to 1s for faster fallback
        "backoff_multiplier": 1.5,  # Reduced from 2 to 1.5 for faster progression
    }

    # Fast connection test timeouts (for initial Scrapli viability testing)
    FAST_TEST_TIMEOUTS = {
        "socket": 8,  # Reduced from 15s to 8s for faster detection
        "transport": 8,  # Reduced from 15s to 8s for faster detection
        "ops": 15,  # Keep ops timeout reasonable for actual commands
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
        "Network is unreachable",
        # Authentication failure patterns - these should fail fast to provide clear errors
        "password prompt seen more than once",
        "authentication failed",
        "auth failed",
        "login failed",
        "access denied",
        "permission denied",
        "authentication error",
        "invalid password",
        "invalid username",
        "login incorrect",
        "authentication timeout",
        "too many authentication failures",
        "authentication attempts exceeded",
    ]

    # Comprehensive platform mappings for better recognition
    # This is the single source of truth for platform name normalization
    PLATFORM_ALIASES = {
        # Cisco IOS variations
        "ios": "cisco_ios",
        "cisco_ios": "cisco_ios",
        "iosxe": "cisco_ios",
        "ios-xe": "cisco_ios",
        "cisco_xe": "cisco_ios",
        "cisco_iosxe": "cisco_ios",
        # Cisco NXOS variations
        "nxos": "cisco_nxos",
        "cisco_nxos": "cisco_nxos",
        "nexus": "cisco_nxos",
        # Cisco IOSXR variations
        "iosxr": "cisco_iosxr",
        "ios-xr": "cisco_iosxr",
        "cisco_iosxr": "cisco_iosxr",
        # Cisco ASA variations
        "asa": "cisco_asa",
        "cisco_asa": "cisco_asa",
        # Other vendor platforms
        "eos": "arista_eos",
        "arista_eos": "arista_eos",
        "junos": "juniper_junos",
        "juniper_junos": "juniper_junos",
        # Generic platforms
        "generic": "generic",
        "autodetect": "autodetect",
    }

    @classmethod
    def get_fast_test_timeouts(cls) -> dict[str, int]:
        """Get fast connection test timeouts for initial viability testing."""
        return cls.FAST_TEST_TIMEOUTS.copy()

    @classmethod
    def should_fast_fail_to_netmiko(cls, error_message: str) -> bool:
        """Check if error message indicates immediate fallback to Netmiko is needed."""
        error_lower = error_message.lower()
        return any(
            pattern.lower() in error_lower for pattern in cls.SCRAPLI_FAST_FAIL_PATTERNS
        )

    @classmethod
    def get_timeouts_for_device(cls, device_type_model: str = "") -> dict[str, int]:
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
        """Normalize platform name using comprehensive aliases.

        This is the single source of truth for platform name normalization
        across the entire plugin. All platform handling should use this method.

        Args:
            platform: Raw platform name (case-insensitive)

        Returns:
            Normalized platform name suitable for connectors and parsers
        """
        if not platform:
            return ""

        # Normalize to lowercase and strip whitespace
        platform_lower = platform.lower().strip()

        # First check direct aliases
        if platform_lower in cls.PLATFORM_ALIASES:
            return cls.PLATFORM_ALIASES[platform_lower]

        # Handle compound platform names (e.g., "cisco ios", "cisco nxos")
        if " " in platform_lower:
            # Split on space and check if first part is "cisco"
            parts = platform_lower.split()
            if len(parts) >= 2 and parts[0] == "cisco":
                # Reconstruct as underscore format (e.g., "cisco ios" -> "cisco_ios")
                reconstructed = "_".join(parts)
                if reconstructed in cls.PLATFORM_ALIASES:
                    return cls.PLATFORM_ALIASES[reconstructed]

        # Handle hyphenated variations (e.g., "ios-xe" -> check "ios_xe")
        if "-" in platform_lower:
            underscore_version = platform_lower.replace("-", "_")
            if underscore_version in cls.PLATFORM_ALIASES:
                return cls.PLATFORM_ALIASES[underscore_version]

        # If no mapping found, return original (for unknown platforms)
        return platform_lower

    @classmethod
    def get_ssh_options(cls) -> dict[str, Any]:
        """Get SSH transport options."""
        return cls.SSH_TRANSPORT_OPTIONS.copy()

    @classmethod
    def get_retry_config(cls) -> dict[str, int]:
        """Get retry configuration."""
        return cls.RETRY_CONFIG.copy()

    @classmethod
    def get_ssh_transport_options(cls) -> dict[str, Any]:
        """Get SSH transport options for Scrapli."""
        user_config = getattr(settings, "PLUGINS_CONFIG", {}).get(
            "netbox_toolkit_plugin", {}
        )
        return {**cls.SSH_TRANSPORT_OPTIONS, **user_config.get("ssh_options", {})}

    @classmethod
    def get_netmiko_config(cls) -> dict[str, Any]:
        """Get Netmiko configuration for fallback connections."""
        user_config = getattr(settings, "PLUGINS_CONFIG", {}).get(
            "netbox_toolkit_plugin", {}
        )
        return {**cls.NETMIKO_CONFIG, **user_config.get("netmiko", {})}

    @classmethod
    def get_security_config(cls) -> dict[str, Any]:
        """Get security configuration for credential encryption."""
        import os

        user_config = getattr(settings, "PLUGINS_CONFIG", {}).get(
            "netbox_toolkit_plugin", {}
        )

        # Merge default config with user overrides
        security_config = {**cls.DEFAULT_SECURITY_CONFIG}
        if "security" in user_config:
            # Deep merge argon2 config
            if "argon2" in user_config["security"]:
                security_config["argon2"].update(user_config["security"]["argon2"])

            # Update other security settings
            for key, value in user_config["security"].items():
                if key != "argon2":
                    security_config[key] = value

        # Handle pepper with flexible configuration priority
        pepper = None

        # Priority 1: Environment variable (most secure)
        if os.getenv("NETBOX_TOOLKIT_PEPPER"):
            pepper = os.getenv("NETBOX_TOOLKIT_PEPPER")

        # Priority 2: Direct configuration in PLUGINS_CONFIG
        elif security_config.get("pepper"):
            pepper = security_config["pepper"]

        # Priority 3: Require explicit configuration (no auto-generation)
        else:
            raise ValueError(
                "REQUIRED: Security pepper must be configured for version 0.1.1 or later.\n"
                "Set either:\n"
                "1. NETBOX_TOOLKIT_PEPPER environment variable (recommended), or\n"
                "2. 'security.pepper' in PLUGINS_CONFIG\n\n"
                'Generate a secure pepper with: python -c "import secrets; print(secrets.token_urlsafe(48))"\n\n'
                "This is a new requirement for encrypted credential storage functionality introduced in version 0.1.1.\n"
                "Store the pepper securely and never commit it to version control."
            )

        if not pepper or len(pepper) < 32:
            raise ValueError(
                "Security pepper must be at least 32 characters long for adequate security"
            )

        security_config["pepper"] = pepper
        return security_config

    @classmethod
    def validate_security_config(cls) -> bool:
        """Validate security configuration and return True if valid."""
        try:
            config = cls.get_security_config()

            # Validate Argon2 parameters
            argon2_config = config["argon2"]

            if argon2_config["time_cost"] < 1:
                raise ValueError("Argon2 time_cost must be at least 1")

            if argon2_config["memory_cost"] < 1024:
                raise ValueError("Argon2 memory_cost must be at least 1024 (1KB)")

            if argon2_config["parallelism"] < 1:
                raise ValueError("Argon2 parallelism must be at least 1")

            if argon2_config["hash_len"] < 16:
                raise ValueError("Argon2 hash_len must be at least 16 bytes")

            if argon2_config["salt_len"] < 8:
                raise ValueError("Argon2 salt_len must be at least 8 bytes")

            return True

        except Exception as e:
            from .utils.logging import get_toolkit_logger

            logger = get_toolkit_logger(__name__)
            logger.error(f"Security configuration validation failed: {e}")
            return False
