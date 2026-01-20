"""Login use case.

Handles user authentication with email and password.
"""
from dataclasses import dataclass
from datetime import timedelta

from src.domain.entities.user import User
from src.domain.exceptions import InvalidCredentialsError, ValidationError
from src.domain.repositories.user_repository import UserRepository


@dataclass
class LoginResult:
    """Result of successful login."""

    user: User
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class Login:
    """Use case for user login authentication."""

    def __init__(
        self,
        user_repository: UserRepository,
        password_hasher: object,  # PasswordHasherProtocol
        jwt_handler: object,  # JWTHandlerProtocol
        access_token_expire_minutes: int = 30,
        refresh_token_expire_days: int = 7,
    ) -> None:
        """Initialize Login use case.

        Args:
            user_repository: Repository for user data access
            password_hasher: Service for password verification
            jwt_handler: Service for JWT token creation
            access_token_expire_minutes: Access token expiration in minutes
            refresh_token_expire_days: Refresh token expiration in days
        """
        self.user_repository = user_repository
        self.password_hasher = password_hasher
        self.jwt_handler = jwt_handler
        self.access_token_expire_minutes = access_token_expire_minutes
        self.refresh_token_expire_days = refresh_token_expire_days

    async def execute(self, email: str, password: str) -> LoginResult:
        """Authenticate user and return tokens.

        Args:
            email: User's email address
            password: User's plain text password

        Returns:
            LoginResult: Contains user, access_token, and refresh_token

        Raises:
            ValidationError: If email or password is empty
            InvalidCredentialsError: If credentials are invalid or user is inactive
        """
        # Validate input
        if not email or not email.strip():
            raise ValidationError("Email is required")

        if not password:
            raise ValidationError("Password is required")

        email = email.strip().lower()

        # Find user by email
        user = await self.user_repository.get_by_email(email)

        if user is None:
            # Don't reveal whether user exists or not for security
            raise InvalidCredentialsError()

        # Check if user is active
        if not user.is_active:
            raise InvalidCredentialsError()

        # Verify password
        if not self.password_hasher.verify_password(password, user.password_hash):
            raise InvalidCredentialsError()

        # Create access token
        access_token = self.jwt_handler.create_access_token(
            user_id=user.id,
            email=user.email,
            role=user.role.value,
            brand_id=user.brand_id,
            expires_delta=timedelta(minutes=self.access_token_expire_minutes),
        )

        # Create refresh token (longer expiration)
        refresh_token = self.jwt_handler.create_access_token(
            user_id=user.id,
            email=user.email,
            role=user.role.value,
            brand_id=user.brand_id,
            expires_delta=timedelta(days=self.refresh_token_expire_days),
        )

        return LoginResult(
            user=user,
            access_token=access_token,
            refresh_token=refresh_token,
        )
