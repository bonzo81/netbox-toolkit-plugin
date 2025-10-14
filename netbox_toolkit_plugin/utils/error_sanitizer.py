"""
Error sanitization utilities for production security
"""

import logging
import re

logger = logging.getLogger(__name__)


class ErrorSanitizer:
    """Utility class for sanitizing error messages in production environments"""

    # Patterns that indicate sensitive information that should be sanitized
    SENSITIVE_PATTERNS = [
        # File paths
        r"/[a-zA-Z0-9_\-/.]+\.py",
        r"[A-Za-z]:\\[a-zA-Z0-9_\-\\/.]+",
        # Database connection strings
        r"postgresql://[^@]+@[^/]+/[^\s]+",
        r"mysql://[^@]+@[^/]+/[^\s]+",
        r"sqlite:///[^\s]+",
        # IP addresses and ports
        r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}:[0-9]+\b",
        # Environment variables and secrets
        r"SECRET_KEY\s*=\s*[^\s]+",
        r"PASSWORD\s*=\s*[^\s]+",
        r"TOKEN\s*=\s*[^\s]+",
        # Stack trace indicators
        r"Traceback \(most recent call last\):",
        r'File "[^"]+", line \d+',
        # Internal module paths
        r"netbox_toolkit_plugin\.[a-zA-Z0-9_.]+",
    ]

    # Generic error messages for different categories
    GENERIC_MESSAGES = {
        "authentication": "Authentication failed. Please check your credentials.",
        "authorization": "You do not have permission to perform this action.",
        "validation": "The provided data is invalid. Please check your input.",
        "connection": "Unable to connect to the target device. Please check network connectivity.",
        "encryption": "Unable to process credentials. Please recreate your credential set.",
        "database": "A database error occurred. Please try again later.",
        "general": "An unexpected error occurred. Please try again later.",
    }

    @classmethod
    def sanitize_error_message(
        cls,
        error_message: str,
        error_category: str | None = None,
        include_hint: bool = False,
    ) -> str:
        """
        Sanitize an error message for safe display to users

        Args:
            error_message: The original error message
            error_category: Category hint for selecting appropriate generic message
            include_hint: Whether to include a sanitized hint about the error

        Returns:
            Sanitized error message safe for display
        """
        if not error_message:
            return cls.GENERIC_MESSAGES["general"]

        # Log the original error for debugging (this should go to secure logs)
        logger.warning(f"Error sanitized: {error_message}")

        # Check if this looks like a sensitive error
        for pattern in cls.SENSITIVE_PATTERNS:
            if re.search(pattern, error_message, re.IGNORECASE):
                # Use generic message based on category
                generic_message = cls.GENERIC_MESSAGES.get(
                    error_category, cls.GENERIC_MESSAGES["general"]
                )

                if include_hint:
                    # Add a sanitized hint about the error type
                    hint = cls._extract_safe_hint(error_message)
                    if hint:
                        generic_message += f" ({hint})"

                return generic_message

        # If no sensitive patterns found, return original message
        # but still apply basic sanitization
        return cls._basic_sanitize(error_message)

    @classmethod
    def _extract_safe_hint(cls, error_message: str) -> str | None:
        """Extract a safe hint about the error type"""
        error_lower = error_message.lower()

        if any(
            keyword in error_lower
            for keyword in ["connection", "timeout", "unreachable"]
        ):
            return "connection issue"
        elif any(
            keyword in error_lower
            for keyword in ["authentication", "login", "credential"]
        ):
            return "authentication issue"
        elif any(
            keyword in error_lower for keyword in ["permission", "denied", "forbidden"]
        ):
            return "permission issue"
        elif any(
            keyword in error_lower for keyword in ["syntax", "invalid", "malformed"]
        ):
            return "format issue"

        return None

    @classmethod
    def _basic_sanitize(cls, message: str) -> str:
        """Apply basic sanitization even to non-sensitive messages"""
        # Remove any remaining file paths
        message = re.sub(r"/[a-zA-Z0-9_\-/.]+\.py", "[file]", message)

        # Remove any IP addresses
        message = re.sub(r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b", "[host]", message)

        # Truncate very long messages
        if len(message) > 200:
            message = message[:197] + "..."

        return message

    @classmethod
    def sanitize_api_error(cls, error: Exception, operation: str = "operation") -> str:
        """
        Sanitize errors specifically for API responses

        Args:
            error: The exception that occurred
            operation: Description of the operation that failed

        Returns:
            Sanitized error message for API response
        """
        error_str = str(error)
        error_type = type(error).__name__

        # Determine error category based on exception type
        category = "general"
        if "Auth" in error_type or "Credential" in error_type:
            category = "authentication"
        elif "Permission" in error_type or "Forbidden" in error_type:
            category = "authorization"
        elif "Connection" in error_type or "Timeout" in error_type:
            category = "connection"
        elif "Validation" in error_type or "Invalid" in error_type:
            category = "validation"

        sanitized = cls.sanitize_error_message(
            error_str, error_category=category, include_hint=True
        )

        return f"Failed to {operation}: {sanitized}"
