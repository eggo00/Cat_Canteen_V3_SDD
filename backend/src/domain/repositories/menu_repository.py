"""MenuRepository interface.

Defines the contract for menu data access operations.
"""
from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.entities.category import Category


class MenuRepository(ABC):
    """Abstract repository interface for Menu operations."""

    @abstractmethod
    async def create_category(
        self, brand_id: UUID, category: Category
    ) -> Category:
        """Create a new category for a brand.

        Args:
            brand_id: Brand UUID
            category: Category entity to create

        Returns:
            Created category with generated ID

        Raises:
            NotFoundError: If brand not found
        """
        pass

    @abstractmethod
    async def get_category_by_id(self, category_id: UUID) -> Category | None:
        """Get category by ID.

        Args:
            category_id: Category UUID

        Returns:
            Category if found, None otherwise
        """
        pass

    @abstractmethod
    async def get_categories_by_brand(
        self, brand_id: UUID, include_items: bool = True
    ) -> list[Category]:
        """Get all categories for a brand.

        Args:
            brand_id: Brand UUID
            include_items: Whether to include menu items

        Returns:
            List of categories ordered by display_order
        """
        pass

    @abstractmethod
    async def update_category(self, category: Category) -> Category:
        """Update an existing category.

        Args:
            category: Category entity with updated data

        Returns:
            Updated category

        Raises:
            NotFoundError: If category not found
        """
        pass

    @abstractmethod
    async def delete_category(self, category_id: UUID) -> bool:
        """Delete a category by ID.

        Args:
            category_id: Category UUID

        Returns:
            True if deleted, False if not found
        """
        pass

    @abstractmethod
    async def upload_menu_json(self, brand_id: UUID, menu_data: dict) -> list[Category]:
        """Upload complete menu from JSON data.

        This method replaces all existing categories and menu items
        for the brand with the new data from JSON.

        Args:
            brand_id: Brand UUID
            menu_data: Menu data in JSON format (validated by MenuEngine)

        Returns:
            List of created categories with items

        Raises:
            NotFoundError: If brand not found
            ValidationError: If menu data is invalid
        """
        pass

    @abstractmethod
    async def get_full_menu(self, brand_id: UUID) -> dict:
        """Get complete menu as JSON for a brand.

        Args:
            brand_id: Brand UUID

        Returns:
            Menu data in JSON format with all categories and items

        Raises:
            NotFoundError: If brand not found
        """
        pass

    @abstractmethod
    async def reorder_categories(
        self, brand_id: UUID, category_order: list[UUID]
    ) -> bool:
        """Reorder categories for a brand.

        Args:
            brand_id: Brand UUID
            category_order: List of category IDs in desired order

        Returns:
            True if successful

        Raises:
            NotFoundError: If brand or any category not found
            ValidationError: If category list is invalid
        """
        pass
