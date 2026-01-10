"""UploadMenu use case.

Handles menu JSON upload and validation.
"""
from typing import Any
from uuid import UUID

from src.domain.entities.category import Category
from src.domain.exceptions import NotFoundError
from src.domain.repositories.brand_repository import BrandRepository
from src.domain.repositories.menu_repository import MenuRepository
from src.domain.services.menu_engine import MenuEngine


class UploadMenu:
    """Use case for uploading menu JSON."""

    def __init__(
        self,
        brand_repository: BrandRepository,
        menu_repository: MenuRepository,
        menu_engine: MenuEngine,
    ) -> None:
        """Initialize UploadMenu use case.

        Args:
            brand_repository: Repository for brand data access
            menu_repository: Repository for menu data access
            menu_engine: Service for menu validation
        """
        self.brand_repository = brand_repository
        self.menu_repository = menu_repository
        self.menu_engine = menu_engine

    async def execute(
        self, brand_id: UUID, menu_data: dict[str, Any]
    ) -> list[Category]:
        """Upload menu JSON for a brand.

        Args:
            brand_id: Brand UUID
            menu_data: Menu data in JSON format

        Returns:
            List of created categories with menu items

        Raises:
            NotFoundError: If brand not found
            ValidationError: If menu data is invalid
        """
        # Verify brand exists
        brand = await self.brand_repository.get_by_id(brand_id)
        if brand is None:
            raise NotFoundError("Brand", str(brand_id))

        # Validate menu JSON
        self.menu_engine.validate_menu_json(menu_data)

        # Upload menu
        categories = await self.menu_repository.upload_menu_json(brand_id, menu_data)

        return categories
