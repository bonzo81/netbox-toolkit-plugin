"""
Enhanced encryption service for secure device credential storage.

This service provides secure encryption and decryption of device credentials
using industry-standard cryptography with Argon2id for key derivation and
token hashing, and HKDF for per-credential key derivation. It includes
pepper-based security enhancements.
"""

import base64
import hashlib
import secrets

from django.conf import settings

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

try:
    import argon2

    HAS_ARGON2 = True
except ImportError:
    HAS_ARGON2 = False


class CredentialEncryptionService:
    """
    Enhanced secure encryption/decryption service for device credentials.

    Features:
    - Fernet (AES-128 CBC + HMAC-SHA256) for credential encryption/decryption
    - Argon2id for master key derivation and token hashing with pepper
    - HKDF for per-credential key derivation
    - Unique encryption keys per credential set
    - Secure token validation with resistance to timing attacks
    - No keys stored in database - all derived deterministically

    Security Model:
    - PEPPER is the PRIMARY secret (must be set via environment/config)
    - SECRET_KEY is SECONDARY (provides defense in depth)
    - Credentials remain secure even if Django SECRET_KEY is compromised
    - Both secrets required for complete compromise (key isolation)

    Important - Secret Rotation:
    Changing PEPPER or SECRET_KEY will make existing encrypted credentials
    inaccessible. This is acceptable since the plugin stores credentials for
    convenience only - they are not the source of truth. Simply recreate the
    DeviceCredentialSet objects with the actual credentials after rotation.

    Recommended Practice:
    - Set PEPPER once during initial deployment
    - Store PEPPER securely (e.g., environment variable, secrets manager)
    - If rotation needed: delete old credentials, users re-enter them
    """

    def __init__(self):
        """Initialize the encryption service with enhanced security configuration."""
        if not HAS_ARGON2:
            raise ImportError(
                "argon2-cffi is required for enhanced security features. "
                "Install with: pip install argon2-cffi"
            )

        # Load security configuration
        from ..settings import ToolkitSettings

        self._security_config = ToolkitSettings.get_security_config()
        self._pepper = self._security_config["pepper"].encode("utf-8")
        self._argon2_config = self._security_config["argon2"]

        # Initialize Argon2 hasher with configured parameters
        self._password_hasher = argon2.PasswordHasher(
            time_cost=self._argon2_config["time_cost"],
            memory_cost=self._argon2_config["memory_cost"],
            parallelism=self._argon2_config["parallelism"],
            hash_len=self._argon2_config["hash_len"],
            salt_len=self._argon2_config["salt_len"],
        )

        # Derive master key using enhanced method
        self._master_key = self._derive_master_key()

    def encrypt_credentials(self, username: str, password: str) -> dict[str, str]:
        """
        Encrypt credentials using Fernet with Argon2id-derived keys.

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

    def encrypt_token(self, raw_token: str) -> str:
        """
        Encrypt a raw token using Fernet with master key.

        Args:
            raw_token: The raw token string to encrypt

        Returns:
            Base64 encoded encrypted token
        """
        # Use master key for token encryption
        fernet = Fernet(self._master_key)

        # Encrypt the raw token
        encrypted_token = fernet.encrypt(raw_token.encode("utf-8"))

        return base64.b64encode(encrypted_token).decode("utf-8")

    def decrypt_token(self, encrypted_token: str) -> str:
        """
        Decrypt an encrypted token.

        Args:
            encrypted_token: Base64 encoded encrypted token

        Returns:
            Decrypted raw token string
        """
        try:
            # Use master key for token decryption
            fernet = Fernet(self._master_key)

            # Decode and decrypt the token
            encrypted_token_bytes = base64.b64decode(encrypted_token.encode("utf-8"))
            decrypted_token = fernet.decrypt(encrypted_token_bytes)

            return decrypted_token.decode("utf-8")

        except Exception as e:
            raise ValueError(f"Failed to decrypt token: {str(e)}") from e

    def generate_access_token(
        self, credential_set_id: int, user_id: int
    ) -> tuple[str, str]:
        """
        Generate a secure credential token with Argon2id hash for storage.

        Args:
            credential_set_id: ID of the credential set
            user_id: ID of the user who owns the credentials

        Returns:
            Tuple of (raw_token, token_hash) where:
            - raw_token: Token to return to user for API calls
            - token_hash: Argon2id hash to store in database
        """
        # Generate random token for user
        raw_token = secrets.token_urlsafe(64)

        # Create token hash with pepper and context for storage
        token_hash = self._hash_token_for_storage(raw_token, credential_set_id, user_id)

        return raw_token, token_hash

    def validate_access_token(
        self, raw_token: str, stored_hash: str, credential_set_id: int, user_id: int
    ) -> bool:
        """
        Validate an access token against its stored Argon2id hash.

        Args:
            raw_token: Token provided by user
            stored_hash: Argon2id hash stored in database
            credential_set_id: ID of the credential set
            user_id: ID of the user

        Returns:
            True if token is valid, False otherwise
        """
        try:
            # Recreate the token context used during hashing
            token_with_context = self._create_token_context(
                raw_token, credential_set_id, user_id
            )

            # Verify using Argon2id - this is timing-attack resistant
            self._password_hasher.verify(stored_hash, token_with_context)
            return True

        except argon2.exceptions.VerifyMismatchError:
            return False
        except Exception:
            # Log but don't expose internal errors
            return False

    def _derive_master_key(self) -> bytes:
        """
        Derive master encryption key using Argon2id with pepper.

        Security Model:
            - Pepper is the PRIMARY secret (from environment or config)
            - SECRET_KEY is SECONDARY (for defense in depth)
            - This ensures credentials remain secure even if SECRET_KEY is compromised
            - Requires both pepper AND SECRET_KEY for complete compromise

        Returns:
            32-byte key suitable for Fernet encryption
        """
        # Use pepper as primary secret, SECRET_KEY as secondary for defense in depth
        # This isolates credential encryption from Django's SECRET_KEY
        primary_secret = self._pepper
        secondary_secret = settings.SECRET_KEY.encode("utf-8")

        # Service-specific salt to prevent key reuse
        salt = b"netbox_toolkit_credentials_v2"

        # Check if we should use Argon2id or fall back to PBKDF2
        if self._security_config.get("master_key_derivation") == "argon2id":
            # Combine secrets with pepper as primary component
            key_material = primary_secret + secondary_secret + salt

            # Use lower parameters for master key derivation (performance)
            derived_key_raw = argon2.low_level.hash_secret_raw(
                secret=key_material,
                salt=salt[:16],  # Argon2 needs exactly 16 bytes for salt
                time_cost=2,  # Lower than token hashing
                memory_cost=8192,  # 8MB for master key
                parallelism=1,
                hash_len=32,
                type=argon2.low_level.Type.ID,
            )
        else:
            # Fallback to PBKDF2 for compatibility
            key_material = primary_secret + secondary_secret
            derived_key_raw = hashlib.pbkdf2_hmac(
                "sha256",
                key_material,
                salt,
                100000,  # 100k iterations
            )

        # Encode for Fernet (base64url)
        return base64.urlsafe_b64encode(derived_key_raw)

    def _derive_credential_key(self, key_id: str) -> bytes:
        """
        Derive a unique encryption key for a specific credential set.

        Uses HKDF (HMAC-based Key Derivation Function) with SHA256 for
        cryptographically secure key derivation. This is superior to
        simple hashing as it provides proper key stretching and domain
        separation.

        Args:
            key_id: Unique identifier for this credential set

        Returns:
            32-byte key suitable for Fernet encryption
        """
        # Use HKDF for proper cryptographic key derivation
        # This provides defense-in-depth over simple SHA256 hashing
        hkdf = HKDF(
            algorithm=hashes.SHA256(),
            length=32,  # 32 bytes for Fernet
            salt=None,  # Master key already salted via Argon2id
            info=key_id.encode("utf-8"),  # Domain separation per credential
        )

        derived_key = hkdf.derive(self._master_key)

        # Encode for Fernet (base64url)
        return base64.urlsafe_b64encode(derived_key)

    def validate_token_format(self, token: str) -> bool:
        """
        Validate that a token has the expected format.

        Args:
            token: Raw token to validate (not the hash)

        Returns:
            True if token format is valid
        """
        if not token or not isinstance(token, str):
            return False

        # Check length (URL-safe base64 tokens are typically 86 chars for 64 bytes)
        if len(token) < 40 or len(token) > 128:
            return False

        # Check that it contains only URL-safe base64 characters
        import string

        valid_chars = string.ascii_letters + string.digits + "-_"
        return all(c in valid_chars for c in token)

    def _create_token_context(
        self, raw_token: str, credential_set_id: int, user_id: int
    ) -> str:
        """
        Create token context string for hashing with pepper and metadata.

        Args:
            raw_token: The raw token string
            credential_set_id: ID of the credential set
            user_id: ID of the user

        Returns:
            Context string for hashing
        """
        # Include pepper and context to prevent token reuse across different contexts
        context_data = f"{raw_token}:{credential_set_id}:{user_id}"
        return context_data + ":" + self._pepper.decode("utf-8")

    def _hash_token_for_storage(
        self, raw_token: str, credential_set_id: int, user_id: int
    ) -> str:
        """
        Hash a token with context for secure storage.

        Args:
            raw_token: The raw token to hash
            credential_set_id: ID of the credential set
            user_id: ID of the user

        Returns:
            Argon2id hash suitable for database storage
        """
        token_with_context = self._create_token_context(
            raw_token, credential_set_id, user_id
        )
        return self._password_hasher.hash(token_with_context)
