"""BrandRepository implementation using SQLAlchemy.

Provides persistence for Brand entities.
"""
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.brand import Brand
from src.domain.repositories.brand_repository import BrandRepository
from src.infrastructure.database.models.brand_model import BrandModel


class BrandRepositoryImpl(BrandRepository):
    """SQLAlchemy implementation of BrandRepository."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize repository.

        Args:
            session: Async SQLAlchemy session
        """
        self.session = session

    async def create(self, brand: Brand) -> Brand:
        """Create a new brand.

        Args:
            brand: Brand entity to create

        Returns:
            Created brand with database-generated fields
        """
        # Convert entity to model
        brand_model = BrandModel(
            id=brand.id,
            name=brand.name,
            slug=brand.slug,
            description=brand.description,
            logo_url=brand.logo_url,
            theme_config=brand.theme_config.to_dict(),
            is_active=brand.is_active,
        )

        self.session.add(brand_model)
        await self.session.flush()
        await self.session.refresh(brand_model)

        # Convert model back to entity
        return self._to_entity(brand_model)

    async def get_by_id(self, brand_id: UUID) -> Brand | None:
        """Get brand by ID.

        Args:
            brand_id: Brand UUID

        Returns:
            Brand if found, None otherwise
        """
        stmt = select(BrandModel).where(BrandModel.id == brand_id)
        result = await self.session.execute(stmt)
        brand_model = result.scalar_one_or_none()

        if brand_model is None:
            return None

        return self._to_entity(brand_model)

    async def get_by_slug(self, slug: str) -> Brand | None:
        """Get brand by slug.

        Args:
            slug: Brand slug

        Returns:
            Brand if found, None otherwise
        """
        stmt = select(BrandModel).where(BrandModel.slug == slug)
        result = await self.session.execute(stmt)
        brand_model = result.scalar_one_or_none()

        if brand_model is None:
            return None

        return self._to_entity(brand_model)

    async def get_all(self, skip: int = 0, limit: int = 100) -> list[Brand]:
        """Get all brands with pagination.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of brands
        """
        stmt = select(BrandModel).offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        brand_models = result.scalars().all()

        return [self._to_entity(model) for model in brand_models]

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
        stmt = (
            select(BrandModel)
            .where(BrandModel.is_active == True)
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        brand_models = result.scalars().all()

        return [self._to_entity(model) for model in brand_models]

    async def update(self, brand: Brand) -> Brand:
        """Update an existing brand.

        Args:
            brand: Brand entity with updated data

        Returns:
            Updated brand
        """
        stmt = select(BrandModel).where(BrandModel.id == brand.id)
        result = await self.session.execute(stmt)
        brand_model = result.scalar_one_or_none()

        if brand_model is None:
            from src.domain.exceptions import NotFoundError

            raise NotFoundError("Brand", str(brand.id))

        # Update model fields
        brand_model.name = brand.name
        brand_model.slug = brand.slug
        brand_model.description = brand.description
        brand_model.logo_url = brand.logo_url
        brand_model.theme_config = brand.theme_config.to_dict()
        brand_model.is_active = brand.is_active

        await self.session.flush()
        await self.session.refresh(brand_model)

        return self._to_entity(brand_model)

    async def delete(self, brand_id: UUID) -> bool:
        """Delete a brand by ID.

        Args:
            brand_id: Brand UUID

        Returns:
            True if deleted, False if not found
        """
        stmt = select(BrandModel).where(BrandModel.id == brand_id)
        result = await self.session.execute(stmt)
        brand_model = result.scalar_one_or_none()

        if brand_model is None:
            return False

        await self.session.delete(brand_model)
        await self.session.flush()

        return True

    async def exists_by_slug(self, slug: str) -> bool:
        """Check if a brand with given slug exists.

        Args:
            slug: Brand slug to check

        Returns:
            True if exists, False otherwise
        """
        stmt = select(BrandModel.id).where(BrandModel.slug == slug)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() is not None

    def _to_entity(self, model: BrandModel) -> Brand:
        """Convert BrandModel to Brand entity.

        Args:
            model: BrandModel instance

        Returns:
            Brand entity
        """
        return Brand(
            id=model.id,
            name=model.name,
            slug=model.slug,
            description=model.description,
            logo_url=model.logo_url,
            theme_config=model.theme_config,
            is_active=model.is_active,
        )
