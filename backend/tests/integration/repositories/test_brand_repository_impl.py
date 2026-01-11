"""Integration tests for BrandRepository implementation.

Tests the SQLAlchemy-based BrandRepository against a real database.
"""
import pytest
from uuid import uuid4


class TestBrandRepositoryImpl:
    """Test BrandRepository implementation."""

    async def test_create_brand(self, async_session):
        """Test creating a brand."""
        from src.domain.entities.brand import Brand
        from src.infrastructure.repositories.brand_repository_impl import (
            BrandRepositoryImpl,
        )

        # Arrange
        repository = BrandRepositoryImpl(async_session)
        brand = Brand(
            name="測試餐廳",
            slug="test-restaurant",
            theme_config={"primaryColor": "#FF6B6B"},
        )

        # Act
        created_brand = await repository.create(brand)

        # Assert
        assert created_brand.id is not None
        assert created_brand.name == "測試餐廳"
        assert created_brand.slug == "test-restaurant"

    async def test_get_brand_by_id(self, async_session):
        """Test getting brand by ID."""
        from src.domain.entities.brand import Brand
        from src.infrastructure.repositories.brand_repository_impl import (
            BrandRepositoryImpl,
        )

        # Arrange
        repository = BrandRepositoryImpl(async_session)
        brand = Brand(
            name="測試餐廳",
            slug="test-restaurant",
            theme_config={"primaryColor": "#FF6B6B"},
        )
        created_brand = await repository.create(brand)

        # Act
        retrieved_brand = await repository.get_by_id(created_brand.id)

        # Assert
        assert retrieved_brand is not None
        assert retrieved_brand.id == created_brand.id
        assert retrieved_brand.name == "測試餐廳"

    async def test_get_brand_by_slug(self, async_session):
        """Test getting brand by slug."""
        from src.domain.entities.brand import Brand
        from src.infrastructure.repositories.brand_repository_impl import (
            BrandRepositoryImpl,
        )

        # Arrange
        repository = BrandRepositoryImpl(async_session)
        brand = Brand(
            name="測試餐廳",
            slug="test-restaurant",
            theme_config={"primaryColor": "#FF6B6B"},
        )
        await repository.create(brand)

        # Act
        retrieved_brand = await repository.get_by_slug("test-restaurant")

        # Assert
        assert retrieved_brand is not None
        assert retrieved_brand.slug == "test-restaurant"
        assert retrieved_brand.name == "測試餐廳"

    async def test_get_brand_by_nonexistent_slug_returns_none(self, async_session):
        """Test getting non-existent brand returns None."""
        from src.infrastructure.repositories.brand_repository_impl import (
            BrandRepositoryImpl,
        )

        # Arrange
        repository = BrandRepositoryImpl(async_session)

        # Act
        retrieved_brand = await repository.get_by_slug("nonexistent")

        # Assert
        assert retrieved_brand is None

    async def test_exists_by_slug(self, async_session):
        """Test checking if slug exists."""
        from src.domain.entities.brand import Brand
        from src.infrastructure.repositories.brand_repository_impl import (
            BrandRepositoryImpl,
        )

        # Arrange
        repository = BrandRepositoryImpl(async_session)
        brand = Brand(
            name="測試餐廳",
            slug="test-restaurant",
            theme_config={"primaryColor": "#FF6B6B"},
        )
        await repository.create(brand)

        # Act & Assert
        assert await repository.exists_by_slug("test-restaurant") is True
        assert await repository.exists_by_slug("nonexistent") is False

    async def test_get_all_brands(self, async_session):
        """Test getting all brands with pagination."""
        from src.domain.entities.brand import Brand
        from src.infrastructure.repositories.brand_repository_impl import (
            BrandRepositoryImpl,
        )

        # Arrange
        repository = BrandRepositoryImpl(async_session)
        brand1 = Brand(
            name="餐廳1", slug="restaurant-1", theme_config={"primaryColor": "#FF6B6B"}
        )
        brand2 = Brand(
            name="餐廳2", slug="restaurant-2", theme_config={"primaryColor": "#4ECDC4"}
        )
        await repository.create(brand1)
        await repository.create(brand2)

        # Act
        brands = await repository.get_all(skip=0, limit=10)

        # Assert
        assert len(brands) == 2
        assert brands[0].slug in ["restaurant-1", "restaurant-2"]

    async def test_get_active_brands_only(self, async_session):
        """Test getting only active brands."""
        from src.domain.entities.brand import Brand
        from src.infrastructure.repositories.brand_repository_impl import (
            BrandRepositoryImpl,
        )

        # Arrange
        repository = BrandRepositoryImpl(async_session)
        active_brand = Brand(
            name="活躍餐廳",
            slug="active",
            theme_config={"primaryColor": "#FF6B6B"},
            is_active=True,
        )
        inactive_brand = Brand(
            name="停用餐廳",
            slug="inactive",
            theme_config={"primaryColor": "#4ECDC4"},
            is_active=False,
        )
        await repository.create(active_brand)
        await repository.create(inactive_brand)

        # Act
        active_brands = await repository.get_active_brands(skip=0, limit=10)

        # Assert
        assert len(active_brands) == 1
        assert active_brands[0].slug == "active"

    async def test_update_brand(self, async_session):
        """Test updating a brand."""
        from src.domain.entities.brand import Brand
        from src.infrastructure.repositories.brand_repository_impl import (
            BrandRepositoryImpl,
        )

        # Arrange
        repository = BrandRepositoryImpl(async_session)
        brand = Brand(
            name="原始餐廳",
            slug="original",
            theme_config={"primaryColor": "#FF6B6B"},
        )
        created_brand = await repository.create(brand)

        # Update brand
        created_brand.name = "更新餐廳"
        created_brand.update_theme({"primaryColor": "#00FF00"})

        # Act
        updated_brand = await repository.update(created_brand)

        # Assert
        assert updated_brand.name == "更新餐廳"
        assert updated_brand.theme_config.primary_color == "#00FF00"

    async def test_delete_brand(self, async_session):
        """Test deleting a brand."""
        from src.domain.entities.brand import Brand
        from src.infrastructure.repositories.brand_repository_impl import (
            BrandRepositoryImpl,
        )

        # Arrange
        repository = BrandRepositoryImpl(async_session)
        brand = Brand(
            name="測試餐廳",
            slug="test-restaurant",
            theme_config={"primaryColor": "#FF6B6B"},
        )
        created_brand = await repository.create(brand)

        # Act
        result = await repository.delete(created_brand.id)

        # Assert
        assert result is True
        retrieved_brand = await repository.get_by_id(created_brand.id)
        assert retrieved_brand is None

    async def test_delete_nonexistent_brand_returns_false(self, async_session):
        """Test deleting non-existent brand returns False."""
        from src.infrastructure.repositories.brand_repository_impl import (
            BrandRepositoryImpl,
        )

        # Arrange
        repository = BrandRepositoryImpl(async_session)
        nonexistent_id = uuid4()

        # Act
        result = await repository.delete(nonexistent_id)

        # Assert
        assert result is False
