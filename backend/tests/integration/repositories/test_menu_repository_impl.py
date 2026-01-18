"""Integration tests for MenuRepository implementation.

Tests the SQLAlchemy-based MenuRepository against a real database.
"""
import pytest
from uuid import uuid4


class TestMenuRepositoryImpl:
    """Test MenuRepository implementation."""

    @pytest.fixture
    async def sample_brand(self, async_session):
        """Create a sample brand for testing."""
        from src.domain.entities.brand import Brand
        from src.infrastructure.repositories.brand_repository_impl import (
            BrandRepositoryImpl,
        )

        repository = BrandRepositoryImpl(async_session)
        brand = Brand(
            name="測試餐廳",
            slug="test-restaurant",
            theme_config={"primaryColor": "#FF6B6B"},
        )
        return await repository.create(brand)

    async def test_upload_menu_json(self, async_session, sample_brand):
        """Test uploading complete menu from JSON."""
        from src.infrastructure.repositories.menu_repository_impl import (
            MenuRepositoryImpl,
        )

        # Arrange
        repository = MenuRepositoryImpl(async_session)
        menu_data = {
            "categories": [
                {
                    "name": "飲料",
                    "description": "各式飲品",
                    "display_order": 1,
                    "menuItems": [
                        {
                            "name": "美式咖啡",
                            "description": "香醇美式咖啡",
                            "price": 100.00,
                            "display_order": 1,
                        },
                        {
                            "name": "拿鐵咖啡",
                            "description": "濃郁拿鐵",
                            "price": 120.00,
                            "display_order": 2,
                        },
                    ],
                },
                {
                    "name": "甜點",
                    "description": "美味甜點",
                    "display_order": 2,
                    "menuItems": [
                        {
                            "name": "提拉米蘇",
                            "price": 150.00,
                            "display_order": 1,
                        }
                    ],
                },
            ]
        }

        # Act
        categories = await repository.upload_menu_json(sample_brand.id, menu_data)

        # Assert
        assert len(categories) == 2
        assert categories[0].name == "飲料"
        assert len(categories[0].menu_items) == 2
        assert categories[0].menu_items[0].name == "美式咖啡"
        assert categories[0].menu_items[0].price == 100.00
        assert categories[1].name == "甜點"
        assert len(categories[1].menu_items) == 1

    async def test_upload_menu_json_replaces_existing(
        self, async_session, sample_brand
    ):
        """Test that uploading menu replaces existing menu."""
        from src.infrastructure.repositories.menu_repository_impl import (
            MenuRepositoryImpl,
        )

        # Arrange
        repository = MenuRepositoryImpl(async_session)

        # First upload
        menu_data_v1 = {
            "categories": [
                {
                    "name": "舊分類",
                    "display_order": 1,
                    "menuItems": [
                        {"name": "舊品項", "price": 50.00, "display_order": 1}
                    ],
                }
            ]
        }
        await repository.upload_menu_json(sample_brand.id, menu_data_v1)

        # Second upload (should replace)
        menu_data_v2 = {
            "categories": [
                {
                    "name": "新分類",
                    "display_order": 1,
                    "menuItems": [
                        {"name": "新品項", "price": 100.00, "display_order": 1}
                    ],
                }
            ]
        }

        # Act
        categories = await repository.upload_menu_json(sample_brand.id, menu_data_v2)

        # Assert
        assert len(categories) == 1
        assert categories[0].name == "新分類"
        assert categories[0].menu_items[0].name == "新品項"

        # Verify old data is gone
        full_menu = await repository.get_full_menu(sample_brand.id)
        assert len(full_menu["categories"]) == 1
        assert full_menu["categories"][0]["name"] == "新分類"

    async def test_get_full_menu(self, async_session, sample_brand):
        """Test getting complete menu as JSON."""
        from src.infrastructure.repositories.menu_repository_impl import (
            MenuRepositoryImpl,
        )

        # Arrange
        repository = MenuRepositoryImpl(async_session)
        menu_data = {
            "categories": [
                {
                    "name": "飲料",
                    "description": "各式飲品",
                    "display_order": 1,
                    "menuItems": [
                        {
                            "name": "美式咖啡",
                            "description": "香醇美式咖啡",
                            "price": 100.00,
                            "display_order": 1,
                        }
                    ],
                }
            ]
        }
        await repository.upload_menu_json(sample_brand.id, menu_data)

        # Act
        result = await repository.get_full_menu(sample_brand.id)

        # Assert
        assert "categories" in result
        assert len(result["categories"]) == 1
        assert result["categories"][0]["name"] == "飲料"
        assert result["categories"][0]["description"] == "各式飲品"
        assert len(result["categories"][0]["menuItems"]) == 1
        assert result["categories"][0]["menuItems"][0]["name"] == "美式咖啡"

    async def test_get_full_menu_empty(self, async_session, sample_brand):
        """Test getting menu when no menu exists."""
        from src.infrastructure.repositories.menu_repository_impl import (
            MenuRepositoryImpl,
        )

        # Arrange
        repository = MenuRepositoryImpl(async_session)

        # Act
        result = await repository.get_full_menu(sample_brand.id)

        # Assert
        assert result == {"categories": []}

    async def test_create_category(self, async_session, sample_brand):
        """Test creating a category."""
        from src.domain.entities.category import Category
        from src.infrastructure.repositories.menu_repository_impl import (
            MenuRepositoryImpl,
        )

        # Arrange
        repository = MenuRepositoryImpl(async_session)
        category = Category(name="飲料", display_order=1)

        # Act
        created = await repository.create_category(sample_brand.id, category)

        # Assert
        assert created.id is not None
        assert created.name == "飲料"
        assert created.display_order == 1

    async def test_get_category_by_id(self, async_session, sample_brand):
        """Test getting category by ID."""
        from src.domain.entities.category import Category
        from src.infrastructure.repositories.menu_repository_impl import (
            MenuRepositoryImpl,
        )

        # Arrange
        repository = MenuRepositoryImpl(async_session)
        category = Category(name="飲料", display_order=1)
        created = await repository.create_category(sample_brand.id, category)

        # Act
        retrieved = await repository.get_category_by_id(created.id)

        # Assert
        assert retrieved is not None
        assert retrieved.id == created.id
        assert retrieved.name == "飲料"

    async def test_get_categories_by_brand(self, async_session, sample_brand):
        """Test getting all categories for a brand."""
        from src.domain.entities.category import Category
        from src.infrastructure.repositories.menu_repository_impl import (
            MenuRepositoryImpl,
        )

        # Arrange
        repository = MenuRepositoryImpl(async_session)
        cat1 = Category(name="飲料", display_order=1)
        cat2 = Category(name="甜點", display_order=2)
        await repository.create_category(sample_brand.id, cat1)
        await repository.create_category(sample_brand.id, cat2)

        # Act
        categories = await repository.get_categories_by_brand(sample_brand.id)

        # Assert
        assert len(categories) == 2
        # Should be ordered by display_order
        assert categories[0].name == "飲料"
        assert categories[1].name == "甜點"

    async def test_update_category(self, async_session, sample_brand):
        """Test updating a category."""
        from src.domain.entities.category import Category
        from src.infrastructure.repositories.menu_repository_impl import (
            MenuRepositoryImpl,
        )

        # Arrange
        repository = MenuRepositoryImpl(async_session)
        category = Category(name="飲料", display_order=1)
        created = await repository.create_category(sample_brand.id, category)

        # Update
        created.name = "更新飲料"
        created.display_order = 5

        # Act
        updated = await repository.update_category(created)

        # Assert
        assert updated.name == "更新飲料"
        assert updated.display_order == 5

    async def test_delete_category(self, async_session, sample_brand):
        """Test deleting a category."""
        from src.domain.entities.category import Category
        from src.infrastructure.repositories.menu_repository_impl import (
            MenuRepositoryImpl,
        )

        # Arrange
        repository = MenuRepositoryImpl(async_session)
        category = Category(name="飲料", display_order=1)
        created = await repository.create_category(sample_brand.id, category)

        # Act
        result = await repository.delete_category(created.id)

        # Assert
        assert result is True
        retrieved = await repository.get_category_by_id(created.id)
        assert retrieved is None

    async def test_delete_nonexistent_category_returns_false(self, async_session):
        """Test deleting non-existent category returns False."""
        from src.infrastructure.repositories.menu_repository_impl import (
            MenuRepositoryImpl,
        )

        # Arrange
        repository = MenuRepositoryImpl(async_session)
        nonexistent_id = uuid4()

        # Act
        result = await repository.delete_category(nonexistent_id)

        # Assert
        assert result is False
