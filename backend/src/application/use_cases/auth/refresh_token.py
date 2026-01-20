"""RefreshToken use case.

Handles JWT token refresh for continued authentication.
"""
from dataclasses import dataclass
from datetime import timedelta
from uuid import UUID

from src.domain.exceptions import (
    InvalidTokenError,
    TokenExpiredError,
    UnauthorizedError,
)
from src.domain.repositories.user_repository import UserRepository


@dataclass
class RefreshResult:
    """Result of successful token refresh."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshToken:
    """Use case for refreshing JWT tokens."""

    def __init__(
        self,
        user_repository: UserRepository,
        jwt_handler: object,  # JWTHandlerProtocol
        access_token_expire_minutes: int = 30,
        refresh_token_expire_days: int = 7,
    ) -> None:
        """Initialize RefreshToken use case.

        Args:
            user_repository: Repository for user data access
            jwt_handler: Service for JWT token operations
            access_token_expire_minutes: Access token expiration in minutes
            refresh_token_expire_days: Refresh token expiration in days
        """
        self.user_repository = user_repository
        self.jwt_handler = jwt_handler
        self.access_token_expire_minutes = access_token_expire_minutes
        self.refresh_token_expire_days = refresh_token_expire_days

    async def execute(self, refresh_token: str) -> RefreshResult:
        """Refresh tokens using a valid refresh token.

        Args:
            refresh_token: Valid refresh token

        Returns:
            RefreshResult: Contains new access_token and refresh_token

        Raises:
            InvalidTokenError: If token is invalid
            TokenExpiredError: If token has expired
            UnauthorizedError: If user is no longer active
        """
        # Decode and verify the refresh token
        try:
            payload = self.jwt_handler.decode_token(refresh_token)
        except Exception as e:
            # Check if it's an expiration error
            error_msg = str(e).lower()
            if "expired" in error_msg:
                raise TokenExpiredError()
            raise InvalidTokenError()

        # Extract user info from token
        user_id = payload.get("sub")
        if not user_id:
            raise InvalidTokenError()

        # Verify user still exists and is active
        user = await self.user_repository.get_by_id(UUID(user_id))

        if user is None:
            raise InvalidTokenError()

        if not user.is_active:
            raise UnauthorizedError("User account is deactivated")

        # Create new access token
        new_access_token = self.jwt_handler.create_access_token(
            user_id=user.id,
            email=user.email,
            role=user.role.value,
            brand_id=user.brand_id,
            expires_delta=timedelta(minutes=self.access_token_expire_minutes),
        )

        # Create new refresh token
        new_refresh_token = self.jwt_handler.create_access_token(
            user_id=user.id,
            email=user.email,
            role=user.role.value,
            brand_id=user.brand_id,
            expires_delta=timedelta(days=self.refresh_token_expire_days),
        )

        return RefreshResult(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
        )
