"""JWT token handling for authentication."""
from datetime import datetime, timedelta
from typing import Any
from uuid import UUID

import jwt
from jwt.exceptions import InvalidTokenError

from src.infrastructure.config import settings


class JWTHandler:
    """Handler for creating and verifying JWT tokens."""

    @staticmethod
    def create_access_token(
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
            role: User's role (customer, staff, admin, super_admin)
            brand_id: Optional brand ID for brand-specific users
            expires_delta: Optional custom expiration time

        Returns:
            str: Encoded JWT token
        """
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
            )

        payload = {
            "sub": str(user_id),  # Subject (user ID)
            "email": email,
            "role": role,
            "exp": expire,  # Expiration time
            "iat": datetime.utcnow(),  # Issued at
        }

        # Add brand_id if present (for brand-specific users)
        if brand_id:
            payload["brand_id"] = str(brand_id)

        encoded_jwt = jwt.encode(
            payload,
            settings.JWT_SECRET,
            algorithm=settings.JWT_ALGORITHM,
        )

        return encoded_jwt

    @staticmethod
    def decode_token(token: str) -> dict[str, Any]:
        """Decode and verify a JWT token.

        Args:
            token: JWT token string

        Returns:
            dict: Decoded token payload

        Raises:
            InvalidTokenError: If token is invalid or expired
        """
        try:
            payload = jwt.decode(
                token,
                settings.JWT_SECRET,
                algorithms=[settings.JWT_ALGORITHM],
            )
            return payload
        except InvalidTokenError as e:
            raise InvalidTokenError(f"Invalid token: {e}") from e

    @staticmethod
    def verify_token(token: str) -> bool:
        """Verify if a token is valid.

        Args:
            token: JWT token string

        Returns:
            bool: True if token is valid, False otherwise
        """
        try:
            JWTHandler.decode_token(token)
            return True
        except InvalidTokenError:
            return False

    @staticmethod
    def refresh_token(token: str) -> str:
        """Refresh an existing token with a new expiration time.

        Args:
            token: Existing JWT token

        Returns:
            str: New JWT token with refreshed expiration

        Raises:
            InvalidTokenError: If token is invalid
        """
        payload = JWTHandler.decode_token(token)

        # Create new token with same payload but new expiration
        return JWTHandler.create_access_token(
            user_id=UUID(payload["sub"]),
            email=payload["email"],
            role=payload["role"],
            brand_id=UUID(payload["brand_id"]) if payload.get("brand_id") else None,
        )
