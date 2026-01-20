"""UserRepository interface.

Defines the contract for user data access operations.
"""
from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.entities.user import User, UserRole


class UserRepository(ABC):
    """Abstract repository interface for User entity."""

    @abstractmethod
    async def create(self, user: User) -> User:
        """Create a new user.

        Args:
            user: User entity to create

        Returns:
            Created user with generated ID

        Raises:
            DuplicateEmailError: If email already exists
        """
        pass

    @abstractmethod
    async def get_by_id(self, user_id: UUID) -> User | None:
        """Get user by ID.

        Args:
            user_id: User UUID

        Returns:
            User if found, None otherwise
        """
        pass

    @abstractmethod
    async def get_by_email(self, email: str) -> User | None:
        """Get user by email address.

        Args:
            email: User email address

        Returns:
            User if found, None otherwise
        """
        pass

    @abstractmethod
    async def get_by_brand(
        self,
        brand_id: UUID,
        skip: int = 0,
        limit: int = 100,
        role: UserRole | None = None,
    ) -> list[User]:
        """Get users belonging to a specific brand.

        Args:
            brand_id: Brand UUID to filter by
            skip: Number of records to skip
            limit: Maximum number of records to return
            role: Optional role filter

        Returns:
            List of users for the brand
        """
        pass

    @abstractmethod
    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        role: UserRole | None = None,
        is_active: bool | None = None,
    ) -> list[User]:
        """Get all users with pagination and optional filters.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            role: Optional role filter
            is_active: Optional active status filter

        Returns:
            List of users
        """
        pass

    @abstractmethod
    async def update(self, user: User) -> User:
        """Update an existing user.

        Args:
            user: User entity with updated data

        Returns:
            Updated user

        Raises:
            NotFoundError: If user not found
            DuplicateEmailError: If new email already exists
        """
        pass

    @abstractmethod
    async def delete(self, user_id: UUID) -> bool:
        """Delete a user by ID.

        Args:
            user_id: User UUID

        Returns:
            True if deleted, False if not found
        """
        pass

    @abstractmethod
    async def exists_by_email(self, email: str) -> bool:
        """Check if a user with given email exists.

        Args:
            email: Email address to check

        Returns:
            True if exists, False otherwise
        """
        pass

    @abstractmethod
    async def count_by_brand(
        self,
        brand_id: UUID,
        role: UserRole | None = None,
    ) -> int:
        """Count users in a brand.

        Args:
            brand_id: Brand UUID to count users for
            role: Optional role filter

        Returns:
            Number of users
        """
        pass
