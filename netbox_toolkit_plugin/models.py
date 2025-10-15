from django.db import models
from django.db.models import Q
from django.utils import timezone

from netbox.models import NetBoxModel
from utilities.querysets import RestrictedQuerySet


class Command(NetBoxModel):
    name = models.CharField(max_length=100)
    command = models.TextField()
    description = models.TextField(blank=True)

    # Platform-based association (supports multiple platforms)
    platforms = models.ManyToManyField(
        to="dcim.Platform",
        related_name="toolkit_commands",
        help_text="Platforms this command is designed for (e.g., cisco_ios, cisco_nxos, generic)",
    )

    # Command categorization
    command_type = models.CharField(
        max_length=50,
        choices=[
            ("show", "Show Command"),
            ("config", "Configuration Command"),
        ],
        default="show",
        help_text="Type of command for categorization and permission control",
    )

    class Meta:
        ordering = ["name"]

    def __str__(self):
        try:
            # Safely get platform names, avoiding recursion during deletion
            if hasattr(self, "_state") and self._state.adding:
                # Object is being created, platforms not yet available
                return self.name

            platform_names = []
            try:
                platforms = self.platforms.all()[:3]
                platform_names = [str(p) for p in platforms]

                if self.platforms.count() > 3:
                    platform_names.append(f"+{self.platforms.count() - 3} more")
            except Exception:
                # If there's any issue accessing platforms, just return the name
                return self.name

            if platform_names:
                return f"{self.name} ({', '.join(platform_names)})"
            else:
                return f"{self.name}"
        except Exception:
            # Fallback to just the name if anything goes wrong
            return getattr(self, "name", "Command")

    def get_absolute_url(self):
        """Return the URL for this object"""
        from django.urls import reverse

        return reverse(
            "plugins:netbox_toolkit_plugin:command_detail", kwargs={"pk": self.pk}
        )


class CommandLog(NetBoxModel):
    command = models.ForeignKey(
        to=Command, on_delete=models.CASCADE, related_name="logs"
    )
    device = models.ForeignKey(
        to="dcim.Device", on_delete=models.CASCADE, related_name="command_logs"
    )
    output = models.TextField()
    username = models.CharField(max_length=100)
    execution_time = models.DateTimeField(auto_now_add=True)

    # Execution details
    success = models.BooleanField(default=True)
    error_message = models.TextField(blank=True)
    execution_duration = models.FloatField(
        blank=True, null=True, help_text="Command execution time in seconds"
    )

    def __str__(self):
        return f"{self.command} on {self.device}"

    def get_absolute_url(self):
        """Return the URL for this object"""
        from django.urls import reverse

        return reverse(
            "plugins:netbox_toolkit_plugin:commandlog_view", kwargs={"pk": self.pk}
        )


class CommandVariable(models.Model):
    """Model for defining variables that can be used in commands."""

    command = models.ForeignKey(
        to=Command,
        on_delete=models.CASCADE,
        related_name="variables",
        help_text="The command this variable belongs to",
    )

    name = models.CharField(
        max_length=100,
        help_text="Variable name as used in the command (e.g., 'interface_name')",
    )

    display_name = models.CharField(
        max_length=200,
        help_text="Human-readable variable name shown to users",
    )

    VARIABLE_TYPES = [
        ("text", "Free Text"),
        ("netbox_interface", "Device Interface (Interface Name)"),
        ("netbox_vlan", "VLAN (VLAN ID)"),
        ("netbox_vlan_name", "VLAN (VLAN Name)"),
        ("netbox_ip", "IP Address (without prefix)"),
    ]

    variable_type = models.CharField(
        max_length=50,
        choices=VARIABLE_TYPES,
        default="text",
        help_text="Type of variable - determines the input method and what value is substituted",
    )

    required = models.BooleanField(
        default=True,
        help_text="Whether this variable must be provided to execute the command",
    )

    help_text = models.TextField(
        blank=True,
        help_text="Additional help text shown to users for this variable",
    )

    default_value = models.CharField(
        max_length=200,
        blank=True,
        help_text="Default value for this variable (optional)",
    )

    class Meta:
        ordering = ["command", "name"]
        unique_together = ("command", "name")

    def __str__(self):
        if hasattr(self, "command") and self.command:
            return f"{self.command.name} - {self.display_name}"
        return f"Variable: {self.display_name}"


class DeviceCredentialSetManager(models.Manager):
    """Custom manager for DeviceCredentialSet with platform filtering logic"""

    def get_queryset(self):
        """Return RestrictedQuerySet for NetBox permission compatibility"""
        return RestrictedQuerySet(self.model, using=self._db)

    def for_user_and_device(self, user, device):
        """
        Get credential sets for a specific user and device.

        Returns credential sets that either:
        1. Have no platform associations (universal credentials), or
        2. Include the device's platform

        Args:
            user: The user who owns the credential sets
            device: The device for which credentials are needed

        Returns:
            QuerySet of DeviceCredentialSet objects filtered and ordered by name
        """
        queryset = self.filter(owner=user)

        if device.platform:
            # Include universal credentials OR platform-specific credentials
            queryset = queryset.filter(
                Q(platforms__isnull=True) | Q(platforms=device.platform)
            ).distinct()
        else:
            # If device has no platform, only show universal credentials
            queryset = queryset.filter(platforms__isnull=True)

        return queryset.order_by("name")


class DeviceCredentialSet(NetBoxModel):
    """Stores encrypted device credentials for users with token-based access"""

    # User ownership
    owner = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="device_credentials",
        help_text="User who owns this credential set",
    )

    # Credential identification
    name = models.CharField(
        max_length=100, help_text="User-friendly name for this credential set"
    )
    description = models.TextField(
        blank=True,
        help_text="Optional description of when/where these credentials are used",
    )

    # Platform association (optional - for credential reuse across platforms)
    platforms = models.ManyToManyField(
        "dcim.Platform",
        blank=True,
        related_name="credential_sets",
        help_text="Platforms this credential set applies to (leave empty for all platforms)",
    )

    # Encrypted storage
    encrypted_username = models.TextField(
        help_text="Encrypted username for device authentication"
    )
    encrypted_password = models.TextField(
        help_text="Encrypted password for device authentication"
    )
    encryption_key_id = models.CharField(
        max_length=64, help_text="Identifier for the encryption key used"
    )

    # Credential token (hash only - for verification)
    access_token = models.CharField(
        max_length=128,
        unique=True,
        editable=False,
        help_text="Secure token hash for credential access via API",
    )

    # Encrypted raw token for display purposes
    encrypted_token = models.TextField(
        blank=True,
        editable=False,
        help_text="Encrypted raw token for display in UI",
    )

    # Metadata
    created_at = models.DateTimeField(
        auto_now_add=True, help_text="When this credential set was created"
    )
    last_used = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When this credential set was last used for command execution",
    )
    is_active = models.BooleanField(
        default=True, help_text="Whether this credential set is active and can be used"
    )

    # Custom manager
    objects = DeviceCredentialSetManager()

    class Meta:
        unique_together = [("owner", "name")]
        ordering = ["owner", "name"]
        verbose_name = "Device Credential Set"
        verbose_name_plural = "Device Credential Sets"

    def to_objectchange(self, action, **kwargs):
        """
        Override NetBox's ObjectChange creation to prevent sensitive credential data from appearing in changelog.
        Creates a sanitized ObjectChange that doesn't expose encrypted fields.
        """
        # Import required modules
        from django.contrib.contenttypes.models import ContentType

        # Get content type for this model
        content_type = ContentType.objects.get_for_model(self)

        # Create ObjectChange with correct field names and sanitized data
        from core.models import ObjectChange

        objectchange = ObjectChange(
            time=timezone.now(),
            user_id=kwargs.get("user_id"),
            user_name=kwargs.get("user_name", ""),
            request_id=kwargs.get("request_id"),
            action=action,
            changed_object_type=content_type,
            changed_object_id=self.pk,
            object_repr=str(self),
            # Only include non-sensitive metadata, exclude all encrypted fields
            prechange_data=None,  # No pre-change data for security
            postchange_data={
                "id": self.pk,
                "name": self.name,
                "owner": self.owner_id,
                "description": self.description,
                "created_at": self.created_at.isoformat() if self.created_at else None,
                "last_used": self.last_used.isoformat() if self.last_used else None,
                "is_active": self.is_active,
            },
        )

        return objectchange

    def __str__(self):
        try:
            # Avoid accessing relationships during deletion/complex operations
            if hasattr(self, "_state") and self._state.adding:
                return self.name

            platform_count = self.platforms.count() if hasattr(self, "platforms") else 0
            if platform_count > 0:
                return f"{self.name} ({platform_count} platforms)"
            return f"{self.name} (all platforms)"
        except Exception:
            # Fallback for any issues during string representation
            return getattr(self, "name", "Device Credential Set")

    def get_absolute_url(self):
        """Return the URL for this object"""
        from django.urls import reverse

        return reverse(
            "plugins:netbox_toolkit_plugin:devicecredentialset_detail",
            kwargs={"pk": self.pk},
        )

    def update_last_used(self):
        """Update the last_used timestamp"""

        self.last_used = timezone.now()
        self.save(update_fields=["last_used"])

    @property
    def username(self):
        """
        Get the decrypted username for display purposes.
        Returns the decrypted username or error message if decryption fails.
        """
        try:
            from netbox_toolkit_plugin.services.encryption_service import (
                CredentialEncryptionService,
            )

            encryption_service = CredentialEncryptionService()
            credentials = encryption_service.decrypt_credentials(
                self.encrypted_username, self.encrypted_password, self.encryption_key_id
            )
            return credentials["username"]
        except Exception:
            return "⚠️ Decryption failed - recreate credential set"

    @property
    def raw_token(self):
        """
        Get the decrypted raw token for display purposes.
        Returns the decrypted raw token or None if not available.
        """
        if not self.encrypted_token:
            return None

        try:
            from netbox_toolkit_plugin.services.encryption_service import (
                CredentialEncryptionService,
            )

            encryption_service = CredentialEncryptionService()
            # Use the token-specific encryption method
            return encryption_service.decrypt_token(self.encrypted_token)
        except Exception:
            return None
