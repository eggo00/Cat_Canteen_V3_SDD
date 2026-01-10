"""GetBrandBySlug use case.

Retrieves a brand by its slug identifier.
"""
from src.domain.entities.brand import Brand
from src.domain.repositories.brand_repository import BrandRepository


class GetBrandBySlug:
    """Use case for retrieving a brand by slug."""

    def __init__(self, brand_repository: BrandRepository) -> None:
        """Initialize GetBrandBySlug use case.

        Args:
            brand_repository: Repository for brand data access
        """
        self.brand_repository = brand_repository

    async def execute(self, slug: str) -> Brand | None:
        """Get brand by slug.

        Args:
            slug: Brand slug (URL-safe identifier)

        Returns:
            Brand if found, None otherwise
        """
        brand = await self.brand_repository.get_by_slug(slug)
        return brand
