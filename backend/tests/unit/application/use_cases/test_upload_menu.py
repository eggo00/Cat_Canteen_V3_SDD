"""Unit tests for UploadMenu use case.

Tests menu JSON upload and validation.
"""
import pytest
from unittest.mock import AsyncMock, Mock
from uuid import uuid4


class TestUploadMenu:
    """Test UploadMenu use case."""

    @pytest.fixture
    def mock_brand_repository(self):
        """Create mock BrandRepository."""
        repository = AsyncMock()
        repository.get_by_id = AsyncMock()
        return repository

    @pytest.fixture
    def mock_menu_repository(self):
        """Create mock MenuRepository."""
        repository = AsyncMock()
        repository.upload_menu_json = AsyncMock()
        return repository

    @pytest.fixture
    def mock_menu_engine(self):
        """Create mock MenuEngine."""
        engine = Mock()
        engine.validate_menu_json = Mock(return_value=True)
        return engine

    @pytest.fixture
    def sample_menu_json(self):
        """Sample menu JSON data."""
        return {
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

    async def test_upload_menu_success(
        self,
        mock_brand_repository,
        mock_menu_repository,
        mock_menu_engine,
        sample_menu_json,
    ):
        """Test successfully uploading menu JSON."""
        from src.application.use_cases.upload_menu import UploadMenu
        from src.domain.entities.brand import Brand
        from src.domain.entities.category import Category

        # Arrange
        use_case = UploadMenu(
            brand_repository=mock_brand_repository,
            menu_repository=mock_menu_repository,
            menu_engine=mock_menu_engine,
        )

        brand_id = uuid4()
        brand = Brand(
            id=brand_id,
            name="測試餐廳",
            slug="test-restaurant",
            theme_config={"primaryColor": "#FF6B6B"},
        )
        mock_brand_repository.get_by_id.return_value = brand

        # Mock uploaded categories
        from src.domain.entities.menu_item import MenuItem

        category = Category(
            name="飲料",
            description="各式飲品",
            display_order=1,
            menu_items=[
                MenuItem(
                    name="美式咖啡",
                    description="香醇美式咖啡",
                    price=100.00,
                    display_order=1,
                )
            ],
        )
        mock_menu_repository.upload_menu_json.return_value = [category]

        # Act
        result = await use_case.execute(brand_id, sample_menu_json)

        # Assert
        assert len(result) == 1
        assert result[0].name == "飲料"
        mock_menu_engine.validate_menu_json.assert_called_once_with(sample_menu_json)
        mock_brand_repository.get_by_id.assert_called_once_with(brand_id)
        mock_menu_repository.upload_menu_json.assert_called_once_with(
            brand_id, sample_menu_json
        )

    async def test_upload_menu_brand_not_found(
        self,
        mock_brand_repository,
        mock_menu_repository,
        mock_menu_engine,
        sample_menu_json,
    ):
        """Test uploading menu for non-existent brand fails."""
        from src.application.use_cases.upload_menu import UploadMenu
        from src.domain.exceptions import NotFoundError

        # Arrange
        use_case = UploadMenu(
            brand_repository=mock_brand_repository,
            menu_repository=mock_menu_repository,
            menu_engine=mock_menu_engine,
        )

        brand_id = uuid4()
        mock_brand_repository.get_by_id.return_value = None

        # Act & Assert
        with pytest.raises(NotFoundError):
            await use_case.execute(brand_id, sample_menu_json)

    async def test_upload_menu_validates_json(
        self,
        mock_brand_repository,
        mock_menu_repository,
        mock_menu_engine,
        sample_menu_json,
    ):
        """Test that menu JSON is validated before upload."""
        from src.application.use_cases.upload_menu import UploadMenu
        from src.domain.entities.brand import Brand
        from src.domain.exceptions import ValidationError

        # Arrange
        use_case = UploadMenu(
            brand_repository=mock_brand_repository,
            menu_repository=mock_menu_repository,
            menu_engine=mock_menu_engine,
        )

        brand_id = uuid4()
        brand = Brand(
            id=brand_id,
            name="測試餐廳",
            slug="test-restaurant",
            theme_config={"primaryColor": "#FF6B6B"},
        )
        mock_brand_repository.get_by_id.return_value = brand

        # Mock validation failure
        mock_menu_engine.validate_menu_json.side_effect = ValidationError(
            "Invalid menu JSON"
        )

        # Act & Assert
        with pytest.raises(ValidationError):
            await use_case.execute(brand_id, sample_menu_json)

    async def test_upload_menu_for_inactive_brand(
        self,
        mock_brand_repository,
        mock_menu_repository,
        mock_menu_engine,
        sample_menu_json,
    ):
        """Test can upload menu for inactive brand."""
        from src.application.use_cases.upload_menu import UploadMenu
        from src.domain.entities.brand import Brand
        from src.domain.entities.category import Category

        # Arrange
        use_case = UploadMenu(
            brand_repository=mock_brand_repository,
            menu_repository=mock_menu_repository,
            menu_engine=mock_menu_engine,
        )

        brand_id = uuid4()
        brand = Brand(
            id=brand_id,
            name="測試餐廳",
            slug="test-restaurant",
            theme_config={"primaryColor": "#FF6B6B"},
            is_active=False,  # Inactive brand
        )
        mock_brand_repository.get_by_id.return_value = brand

        from src.domain.entities.menu_item import MenuItem

        category = Category(
            name="飲料",
            display_order=1,
            menu_items=[MenuItem(name="美式咖啡", price=100.00, display_order=1)],
        )
        mock_menu_repository.upload_menu_json.return_value = [category]

        # Act
        result = await use_case.execute(brand_id, sample_menu_json)

        # Assert
        assert len(result) == 1
        # Should still succeed even for inactive brand
