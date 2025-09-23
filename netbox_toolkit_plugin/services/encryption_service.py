"""
Encryption service for secure device credential storage.

This service provides secure encryption and decryption of device credentials
using industry-standard cryptography. It derives unique encryption keys
for each credential set and generates secure credential tokens.
"""

import base64
import hashlib
import secrets

from django.conf import settings

from cryptography.fernet import Fernet


class CredentialEncryptionService:
    """
    Handles secure encryption/decryption of device credentials.

    Uses Fernet (symmetric encryption) with keys derived from Django's SECRET_KEY
    and unique key IDs for each credential set. This ensures:
    - Each credential set has a unique encryption key
    - Keys are deterministically derived from the master secret
    - No keys are stored in the database
    - Strong cryptographic protection of stored credentials
    """

    def __init__(self):
        """Initialize the encryption service with master key derivation."""
        self._master_key = self._derive_master_key()

    def encrypt_credentials(self, username: str, password: str) -> dict[str, str]:
        """
        Encrypt credentials and return encrypted data with key ID.

        Args:
            username: Plain text username
            password: Plain text password

        Returns:
            Dictionary containing:
            - encrypted_username: Base64 encoded encrypted username
            - encrypted_password: Base64 encoded encrypted password
            - key_id: Unique identifier for the encryption key
        """
        # Generate unique key ID for this credential set
        key_id = secrets.token_urlsafe(32)

        # Derive encryption key from master key and key ID
        encryption_key = self._derive_credential_key(key_id)

        # Create Fernet cipher
        fernet = Fernet(encryption_key)

        # Encrypt credentials
        encrypted_username = fernet.encrypt(username.encode("utf-8"))
        encrypted_password = fernet.encrypt(password.encode("utf-8"))

        return {
            "encrypted_username": base64.b64encode(encrypted_username).decode("utf-8"),
            "encrypted_password": base64.b64encode(encrypted_password).decode("utf-8"),
            "key_id": key_id,
        }

    def decrypt_credentials(
        self, encrypted_username: str, encrypted_password: str, key_id: str
    ) -> dict[str, str]:
        """
        Decrypt credentials using the provided key ID.

        Args:
            encrypted_username: Base64 encoded encrypted username
            encrypted_password: Base64 encoded encrypted password
            key_id: Key identifier used during encryption

        Returns:
            Dictionary containing:
            - username: Decrypted username
            - password: Decrypted password

        Raises:
            ValueError: If decryption fails or key ID is invalid
        """
        try:
            # Derive the same encryption key using key ID
            encryption_key = self._derive_credential_key(key_id)

            # Create Fernet cipher
            fernet = Fernet(encryption_key)

            # Decode and decrypt credentials
            encrypted_username_bytes = base64.b64decode(
                encrypted_username.encode("utf-8")
            )
            encrypted_password_bytes = base64.b64decode(
                encrypted_password.encode("utf-8")
            )

            decrypted_username = fernet.decrypt(encrypted_username_bytes)
            decrypted_password = fernet.decrypt(encrypted_password_bytes)

            return {
                "username": decrypted_username.decode("utf-8"),
                "password": decrypted_password.decode("utf-8"),
            }

        except Exception as e:
            raise ValueError(f"Failed to decrypt credentials: {str(e)}") from e

    def generate_access_token(self) -> str:
        """
        Generate a secure credential token for API access.

        Returns:
            URL-safe random token string
        """
        return secrets.token_urlsafe(64)

    def _derive_master_key(self) -> bytes:
        """
        Derive master encryption key from Django's SECRET_KEY.

        Returns:
            32-byte key suitable for Fernet encryption
        """
        # Use Django's SECRET_KEY as the base for key derivation
        secret_key = settings.SECRET_KEY.encode("utf-8")

        # Add a service-specific salt to prevent key reuse
        salt = b"netbox_toolkit_credentials_v1"

        # Derive a 32-byte key using SHA-256
        derived_key = hashlib.pbkdf2_hmac(
            "sha256",
            secret_key,
            salt,
            100000,  # 100k iterations for security
        )

        # Encode for Fernet (base64url)
        return base64.urlsafe_b64encode(derived_key)

    def _derive_credential_key(self, key_id: str) -> bytes:
        """
        Derive a unique encryption key for a specific credential set.

        Args:
            key_id: Unique identifier for this credential set

        Returns:
            32-byte key suitable for Fernet encryption
        """
        # Combine master key with key ID to create unique key
        key_material = self._master_key + key_id.encode("utf-8")

        # Hash to get consistent 32-byte key
        key_hash = hashlib.sha256(key_material).digest()

        # Encode for Fernet (base64url)
        return base64.urlsafe_b64encode(key_hash)

    def validate_token_format(self, token: str) -> bool:
        """
        Validate that a token has the expected format.

        Args:
            token: Token to validate

        Returns:
            True if token format is valid
        """
        if not token or not isinstance(token, str):
            return False

        # Check length (URL-safe base64 tokens are typically 86 chars for 64 bytes)
        if len(token) < 40 or len(token) > 128:
            return False

        # Check character set (URL-safe base64)
        allowed_chars = set(
            "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_"
        )
        return all(c in allowed_chars for c in token)
