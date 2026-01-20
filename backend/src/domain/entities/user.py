"""User Entity - Domain Model.

Represents a user in the white-label ordering system with role-based access control.
"""
import re
from datetime import datetime
from enum import Enum
from uuid import UUID, uuid4

from src.domain.exceptions import ValidationError


class UserRole(str, Enum):
    """User roles for role-based access control (RBAC).

    Roles hierarchy (from lowest to highest privilege):
    - CUSTOMER: Can place orders, view own order history
    - STAFF: Can manage orders for their brand
    - ADMIN: Can manage menu, categories, and orders for their brand
    - SUPER_ADMIN: Can manage all brands and users (platform administrator)
    """

    CUSTOMER = "customer"
    STAFF = "staff"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"


class User:
    """User entity representing a system user.

    Users are associated with a specific brand (except super_admin)
    and have role-based permissions for accessing system resources.
    """

    # Email validation regex
    EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")

    def __init__(
        self,
        email: str,
        password_hash: str,
        role: UserRole | str,
        id: UUID | None = None,
        brand_id: UUID | None = None,
        name: str | None = None,
        is_active: bool = True,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ):
        """Initialize a User entity.

        Args:
            email: User email address (unique, required)
            password_hash: Hashed password (required, should be bcrypt)
            role: User role for access control
            id: Unique identifier (auto-generated if not provided)
            brand_id: Associated brand ID (required for non-super_admin users)
            name: Display name (optional)
            is_active: Whether user account is active (default: True)
            created_at: Account creation timestamp
            updated_at: Last update timestamp

        Raises:
            ValidationError: If validation fails
        """
        # Validate email
        if not email or not email.strip():
            raise ValidationError("Email is required")

        email = email.strip().lower()
        if not self.EMAIL_REGEX.match(email):
            raise ValidationError(f"Invalid email format: {email}")

        if len(email) > 255:
            raise ValidationError(
                f"Email too long (max 255 characters, got {len(email)})"
            )

        # Validate password_hash
        if not password_hash or not password_hash.strip():
            raise ValidationError("Password hash is required")

        # Validate and normalize role
        if isinstance(role, str):
            try:
                role = UserRole(role.lower())
            except ValueError:
                valid_roles = [r.value for r in UserRole]
                raise ValidationError(
                    f"Invalid role: {role}. Valid roles: {valid_roles}"
                )

        # Validate brand_id requirement based on role
        if role != UserRole.SUPER_ADMIN and brand_id is None:
            raise ValidationError(
                f"brand_id is required for users with role '{role.value}'"
            )

        # Validate name length if provided
        if name and len(name) > 255:
            raise ValidationError(
                f"Name too long (max 255 characters, got {len(name)})"
            )

        # Set attributes
        self.id = id or uuid4()
        self.email = email
        self.password_hash = password_hash
        self.role = role
        self.brand_id = brand_id
        self.name = name.strip() if name else None
        self.is_active = is_active
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    def update_password(self, new_password_hash: str) -> None:
        """Update user password hash.

        Args:
            new_password_hash: New hashed password

        Raises:
            ValidationError: If password hash is empty
        """
        if not new_password_hash or not new_password_hash.strip():
            raise ValidationError("Password hash is required")

        self.password_hash = new_password_hash
        self.updated_at = datetime.utcnow()

    def update_role(self, new_role: UserRole | str) -> None:
        """Update user role.

        Args:
            new_role: New user role

        Raises:
            ValidationError: If role is invalid or brand_id constraint violated
        """
        if isinstance(new_role, str):
            try:
                new_role = UserRole(new_role.lower())
            except ValueError:
                valid_roles = [r.value for r in UserRole]
                raise ValidationError(
                    f"Invalid role: {new_role}. Valid roles: {valid_roles}"
                )

        # Check brand_id constraint
        if new_role != UserRole.SUPER_ADMIN and self.brand_id is None:
            raise ValidationError(
                f"Cannot change role to '{new_role.value}' without brand_id"
            )

        self.role = new_role
        self.updated_at = datetime.utcnow()

    def activate(self) -> None:
        """Activate the user account."""
        self.is_active = True
        self.updated_at = datetime.utcnow()

    def deactivate(self) -> None:
        """Deactivate the user account."""
        self.is_active = False
        self.updated_at = datetime.utcnow()

    def can_access_brand(self, brand_id: UUID) -> bool:
        """Check if user can access a specific brand.

        Args:
            brand_id: Brand ID to check access for

        Returns:
            bool: True if user can access the brand
        """
        # Super admins can access all brands
        if self.role == UserRole.SUPER_ADMIN:
            return True

        # Other users can only access their assigned brand
        return self.brand_id == brand_id

    def has_permission(self, required_role: UserRole) -> bool:
        """Check if user has at least the required role level.

        Role hierarchy: CUSTOMER < STAFF < ADMIN < SUPER_ADMIN

        Args:
            required_role: Minimum required role

        Returns:
            bool: True if user's role meets or exceeds required role
        """
        role_hierarchy = {
            UserRole.CUSTOMER: 1,
            UserRole.STAFF: 2,
            UserRole.ADMIN: 3,
            UserRole.SUPER_ADMIN: 4,
        }

        return role_hierarchy[self.role] >= role_hierarchy[required_role]

    def is_super_admin(self) -> bool:
        """Check if user is a super admin.

        Returns:
            bool: True if user has SUPER_ADMIN role
        """
        return self.role == UserRole.SUPER_ADMIN

    def is_admin(self) -> bool:
        """Check if user is an admin (or higher).

        Returns:
            bool: True if user has ADMIN or SUPER_ADMIN role
        """
        return self.role in (UserRole.ADMIN, UserRole.SUPER_ADMIN)

    def is_staff(self) -> bool:
        """Check if user is staff (or higher).

        Returns:
            bool: True if user has STAFF, ADMIN, or SUPER_ADMIN role
        """
        return self.role in (UserRole.STAFF, UserRole.ADMIN, UserRole.SUPER_ADMIN)

    def __repr__(self) -> str:
        """String representation of User."""
        return (
            f"<User(id={self.id}, email={self.email}, "
            f"role={self.role.value}, active={self.is_active})>"
        )

    def __eq__(self, other: object) -> bool:
        """Compare two users for equality (by ID).

        Args:
            other: Other object to compare

        Returns:
            bool: True if IDs are equal
        """
        if not isinstance(other, User):
            return False
        return self.id == other.id
