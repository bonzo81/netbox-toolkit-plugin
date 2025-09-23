"""
Service for handling credential token operations and validation
"""

from django.contrib.auth.models import User

from ..models import DeviceCredentialSet
from .encryption_service import CredentialEncryptionService


class CredentialService:
    """Service for credential token operations used by both API and GUI"""

    def __init__(self):
        self.encryption_service = CredentialEncryptionService()

    def validate_token_for_user(
        self, access_token: str, user: User
    ) -> tuple[bool, DeviceCredentialSet | None, str | None]:
        """
        Validate a credential token belongs to the specified user

        Returns:
            (is_valid, credential_set, error_message)
        """
        try:
            credential_set = DeviceCredentialSet.objects.get(
                access_token=access_token, owner=user
            )
            return True, credential_set, None
        except DeviceCredentialSet.DoesNotExist:
            return (
                False,
                None,
                "Invalid credential token or token does not belong to current user",
            )
        except Exception as e:
            return False, None, f"Error validating credential token: {str(e)}"

    def get_credentials_by_token(
        self, access_token: str, user: User
    ) -> tuple[bool, dict[str, str] | None, str | None]:
        """
        Retrieve decrypted credentials using credential token

        Returns:
            (success, credentials_dict, error_message)
        """
        is_valid, credential_set, error = self.validate_token_for_user(
            access_token, user
        )

        if not is_valid:
            return False, None, error

        try:
            decrypted_credentials = self.encryption_service.decrypt_credentials(
                credential_set.encrypted_username,
                credential_set.encrypted_password,
                credential_set.encryption_key_id,
            )
            return True, decrypted_credentials, None
        except Exception as e:
            return False, None, f"Error decrypting credentials: {str(e)}"

    def validate_token_for_device(
        self, access_token: str, user: User, device
    ) -> tuple[bool, DeviceCredentialSet | None, str | None]:
        """
        Validate that a credential token can be used for a specific device

        Returns:
            (is_valid, credential_set, error_message)
        """
        is_valid, credential_set, error = self.validate_token_for_user(
            access_token, user
        )

        if not is_valid:
            return False, None, error

        # Check if credential set supports the device's platform
        if device.platform not in credential_set.platforms.all():
            return (
                False,
                None,
                (
                    f"Credential set '{credential_set.name}' does not support "
                    f"platform '{device.platform.name}'"
                ),
            )

        return True, credential_set, None

    def get_credentials_for_device(
        self, access_token: str, user: User, device
    ) -> tuple[bool, dict[str, str] | None, DeviceCredentialSet | None, str | None]:
        """
        Get decrypted credentials for a specific device using token

        Returns:
            (success, credentials_dict, credential_set, error_message)
        """
        is_valid, credential_set, error = self.validate_token_for_device(
            access_token, user, device
        )

        if not is_valid:
            return False, None, None, error

        try:
            decrypted_credentials = self.encryption_service.decrypt_credentials(
                credential_set.encrypted_username,
                credential_set.encrypted_password,
                credential_set.encryption_key_id,
            )
            return True, decrypted_credentials, credential_set, None
        except Exception as e:
            return False, None, None, f"Error decrypting credentials: {str(e)}"

    def regenerate_token(
        self, credential_set_id: int, user: User
    ) -> tuple[bool, str | None, str | None]:
        """
        Regenerate credential token for a credential set

        Returns:
            (success, new_token, error_message)
        """
        try:
            credential_set = DeviceCredentialSet.objects.get(
                id=credential_set_id, owner=user
            )

            new_token = self.encryption_service.generate_access_token()
            credential_set.access_token = new_token
            credential_set.save(update_fields=["access_token"])

            return True, new_token, None
        except DeviceCredentialSet.DoesNotExist:
            return (
                False,
                None,
                "Credential set not found or does not belong to current user",
            )
        except Exception as e:
            return False, None, f"Error regenerating token: {str(e)}"

    def test_credentials_connectivity(
        self, access_token: str, user: User, device, timeout: int = 10
    ) -> tuple[bool, dict | None, str | None]:
        """
        Test connectivity using stored credentials

        Returns:
            (success, result_dict, error_message)
        """
        success, credentials, credential_set, error = self.get_credentials_for_device(
            access_token, user, device
        )

        if not success:
            return False, None, error

        try:
            # Import here to avoid circular imports
            from ..connectors.factory import ConnectorFactory

            connector = ConnectorFactory.create_connector(device.platform.slug)

            # Test connectivity
            result = connector.test_connection(
                host=str(device.primary_ip.address.ip),
                username=credentials["username"],
                password=credentials["password"],
                timeout=timeout,
            )

            return True, result, None

        except Exception as e:
            return False, None, f"Connectivity test failed: {str(e)}"

    def get_user_credential_sets(self, user: User):
        """Get all credential sets for a user"""
        return DeviceCredentialSet.objects.filter(owner=user).prefetch_related(
            "platforms", "tags"
        )

    def get_credential_sets_for_platform(self, user: User, platform):
        """Get credential sets that support a specific platform"""
        return DeviceCredentialSet.objects.filter(
            owner=user, platforms=platform
        ).prefetch_related("platforms", "tags")
