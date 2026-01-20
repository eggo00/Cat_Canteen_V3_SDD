"""AuthService protocol - Application layer interface for authentication.

Defines the contract for authentication services (password hashing, JWT handling).
Concrete implementations are provided in the infrastructure layer.
"""
from dataclasses import dataclass
from datetime import timedelta
from typing import Any, Protocol
from uuid import UUID


@dataclass
class TokenPair:
    """Data class for access and refresh token pair."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


@dataclass
class TokenPayload:
    """Data class for decoded JWT token payload."""

    user_id: UUID
    email: str
    role: str
    brand_id: UUID | None = None


class PasswordHasherProtocol(Protocol):
    """Protocol for password hashing operations."""

    def hash_password(self, password: str) -> str:
        """Hash a plain text password.

        Args:
            password: Plain text password

        Returns:
            str: Hashed password
        """
        ...

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a plain text password against a hashed password.

        Args:
            plain_password: Plain text password to verify
            hashed_password: Hashed password from database

        Returns:
            bool: True if password matches, False otherwise
        """
        ...


class JWTHandlerProtocol(Protocol):
    """Protocol for JWT token operations."""

    def create_access_token(
        self,
        user_id: UUID,
        email: str,
        role: str,
        brand_id: UUID | None = None,
        expires_delta: timedelta | None = None,
    ) -> str:
        """Create a new JWT access token.

        Args:
            user_id: User's UUID
            email: User's email address
            role: User's role
            brand_id: Optional brand ID for brand-specific users
            expires_delta: Optional custom expiration time

        Returns:
            str: Encoded JWT token
        """
        ...

    def decode_token(self, token: str) -> dict[str, Any]:
        """Decode and verify a JWT token.

        Args:
            token: JWT token string

        Returns:
            dict: Decoded token payload

        Raises:
            InvalidTokenError: If token is invalid or expired
        """
        ...

    def verify_token(self, token: str) -> bool:
        """Verify if a token is valid.

        Args:
            token: JWT token string

        Returns:
            bool: True if token is valid, False otherwise
        """
        ...
