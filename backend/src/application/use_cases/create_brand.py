"""CreateBrand use case.

Handles brand creation with validation and slug generation.
"""
from typing import Any

from src.domain.entities.brand import Brand
from src.domain.exceptions import DuplicateSlugError
from src.domain.repositories.brand_repository import BrandRepository
from src.domain.services.menu_engine import MenuEngine
from src.domain.services.theme_engine import ThemeEngine


class CreateBrand:
    """Use case for creating a new brand."""

    def __init__(
        self,
        brand_repository: BrandRepository,
        menu_engine: MenuEngine,
        theme_engine: ThemeEngine,
    ) -> None:
        """Initialize CreateBrand use case.

        Args:
            brand_repository: Repository for brand persistence
            menu_engine: Service for slug generation
            theme_engine: Service for theme validation
        """
        self.brand_repository = brand_repository
        self.menu_engine = menu_engine
        self.theme_engine = theme_engine

    async def execute(self, brand_data: dict[str, Any]) -> Brand:
        """Create a new brand.

        Args:
            brand_data: Brand data dictionary with:
                - name (required): Brand name
                - slug (optional): URL-safe identifier (auto-generated if not provided)
                - theme_config (required): Theme configuration
                - description (optional): Brand description
                - logo_url (optional): Logo URL
                - is_active (optional): Active status (default: True)

        Returns:
            Created Brand entity

        Raises:
            DuplicateSlugError: If slug already exists
            ValidationError: If validation fails
        """
        # Generate slug from name if not provided
        slug = brand_data.get("slug")
        if not slug:
            slug = self.menu_engine.generate_slug(brand_data["name"])
            brand_data["slug"] = slug

        # Validate theme configuration
        theme_config = brand_data.get("theme_config", {})
        self.theme_engine.validate_theme(theme_config)

        # Check if slug already exists
        slug_exists = await self.brand_repository.exists_by_slug(slug)
        if slug_exists:
            raise DuplicateSlugError(slug)

        # Create brand entity
        brand = Brand(**brand_data)

        # Persist brand
        created_brand = await self.brand_repository.create(brand)

        return created_brand
