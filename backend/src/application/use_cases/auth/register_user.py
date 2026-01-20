"""RegisterUser use case.

Handles user registration with validation and password hashing.
"""
from dataclasses import dataclass
from uuid import UUID

from src.domain.entities.user import User, UserRole
from src.domain.exceptions import (
    DuplicateEmailError,
    NotFoundError,
    UnauthorizedError,
    ValidationError,
)
from src.domain.repositories.brand_repository import BrandRepository
from src.domain.repositories.user_repository import UserRepository


@dataclass
class RegisterResult:
    """Result of successful user registration."""

    user: User


class RegisterUser:
    """Use case for registering new users."""

    # Minimum password length
    MIN_PASSWORD_LENGTH = 8

    def __init__(
        self,
        user_repository: UserRepository,
        brand_repository: BrandRepository,
        password_hasher: object,  # PasswordHasherProtocol
    ) -> None:
        """Initialize RegisterUser use case.

        Args:
            user_repository: Repository for user data access
            brand_repository: Repository for brand data access
            password_hasher: Service for password hashing
        """
        self.user_repository = user_repository
        self.brand_repository = brand_repository
        self.password_hasher = password_hasher

    async def execute(
        self,
        email: str,
        password: str,
        role: UserRole | str,
        brand_id: UUID | None = None,
        name: str | None = None,
        current_user: User | None = None,
    ) -> RegisterResult:
        """Register a new user.

        Args:
            email: User's email address (must be unique)
            password: User's plain text password (will be hashed)
            role: User's role for access control
            brand_id: Associated brand ID (required for non-super_admin)
            name: Optional display name
            current_user: Optional current user performing the registration
                         (for permission checks)

        Returns:
            RegisterResult: Contains created user

        Raises:
            ValidationError: If validation fails
            DuplicateEmailError: If email already exists
            NotFoundError: If brand_id is invalid
            UnauthorizedError: If current user lacks permission
        """
        # Validate email
        if not email or not email.strip():
            raise ValidationError("Email is required")

        email = email.strip().lower()

        # Validate password
        if not password:
            raise ValidationError("Password is required")

        if len(password) < self.MIN_PASSWORD_LENGTH:
            raise ValidationError(
                f"Password must be at least {self.MIN_PASSWORD_LENGTH} characters"
            )

        # Normalize role
        if isinstance(role, str):
            try:
                role = UserRole(role.lower())
            except ValueError:
                valid_roles = [r.value for r in UserRole]
                raise ValidationError(
                    f"Invalid role: {role}. Valid roles: {valid_roles}"
                )

        # Permission checks for creating users with elevated roles
        if current_user:
            self._check_permission(current_user, role, brand_id)

        # Validate brand_id for non-super_admin users
        if role != UserRole.SUPER_ADMIN:
            if brand_id is None:
                raise ValidationError(
                    f"brand_id is required for users with role '{role.value}'"
                )

            # Verify brand exists
            brand = await self.brand_repository.get_by_id(brand_id)
            if brand is None:
                raise NotFoundError("Brand", str(brand_id))

        # Check for duplicate email
        if await self.user_repository.exists_by_email(email):
            raise DuplicateEmailError(email)

        # Hash password
        password_hash = self.password_hasher.hash_password(password)

        # Create user entity
        user = User(
            email=email,
            password_hash=password_hash,
            role=role,
            brand_id=brand_id,
            name=name,
            is_active=True,
        )

        # Persist user
        created_user = await self.user_repository.create(user)

        return RegisterResult(user=created_user)

    def _check_permission(
        self,
        current_user: User,
        target_role: UserRole,
        target_brand_id: UUID | None,
    ) -> None:
        """Check if current user can create a user with the target role.

        Permission rules:
        - super_admin: can create any user
        - admin: can create staff/customer in their brand
        - staff/customer: cannot create users

        Args:
            current_user: User performing the action
            target_role: Role of the user being created
            target_brand_id: Brand of the user being created

        Raises:
            UnauthorizedError: If permission check fails
        """
        # Super admin can do anything
        if current_user.is_super_admin():
            return

        # Non-admins cannot create users
        if not current_user.is_admin():
            raise UnauthorizedError("Only admins can create users")

        # Admins cannot create super_admin or other admin users
        if target_role in (UserRole.SUPER_ADMIN, UserRole.ADMIN):
            raise UnauthorizedError(
                f"Cannot create user with role '{target_role.value}'"
            )

        # Admins can only create users in their own brand
        if target_brand_id and target_brand_id != current_user.brand_id:
            raise UnauthorizedError("Cannot create users in other brands")
