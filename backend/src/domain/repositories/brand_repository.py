"""BrandRepository interface.

Defines the contract for brand data access operations.
"""
from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.entities.brand import Brand


class BrandRepository(ABC):
    """Abstract repository interface for Brand entity."""

    @abstractmethod
    async def create(self, brand: Brand) -> Brand:
        """Create a new brand.

        Args:
            brand: Brand entity to create

        Returns:
            Created brand with generated ID

        Raises:
            DuplicateSlugError: If slug already exists
        """
        pass

    @abstractmethod
    async def get_by_id(self, brand_id: UUID) -> Brand | None:
        """Get brand by ID.

        Args:
            brand_id: Brand UUID

        Returns:
            Brand if found, None otherwise
        """
        pass

    @abstractmethod
    async def get_by_slug(self, slug: str) -> Brand | None:
        """Get brand by slug.

        Args:
            slug: Brand slug (URL-safe identifier)

        Returns:
            Brand if found, None otherwise
        """
        pass

    @abstractmethod
    async def get_all(self, skip: int = 0, limit: int = 100) -> list[Brand]:
        """Get all brands with pagination.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of brands
        """
        pass

    @abstractmethod
    async def get_active_brands(
        self, skip: int = 0, limit: int = 100
    ) -> list[Brand]:
        """Get all active brands with pagination.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of active brands
        """
        pass

    @abstractmethod
    async def update(self, brand: Brand) -> Brand:
        """Update an existing brand.

        Args:
            brand: Brand entity with updated data

        Returns:
            Updated brand

        Raises:
            NotFoundError: If brand not found
            DuplicateSlugError: If new slug already exists
        """
        pass

    @abstractmethod
    async def delete(self, brand_id: UUID) -> bool:
        """Delete a brand by ID.

        Args:
            brand_id: Brand UUID

        Returns:
            True if deleted, False if not found
        """
        pass

    @abstractmethod
    async def exists_by_slug(self, slug: str) -> bool:
        """Check if a brand with given slug exists.

        Args:
            slug: Brand slug to check

        Returns:
            True if exists, False otherwise
        """
        pass
