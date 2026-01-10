"""Unit tests for CreateBrand use case.

Tests brand creation business logic.
"""
import pytest
from unittest.mock import AsyncMock, Mock
from uuid import uuid4


class TestCreateBrand:
    """Test CreateBrand use case."""

    @pytest.fixture
    def mock_brand_repository(self):
        """Create mock BrandRepository."""
        repository = AsyncMock()
        repository.exists_by_slug = AsyncMock(return_value=False)
        repository.create = AsyncMock()
        return repository

    @pytest.fixture
    def mock_menu_engine(self):
        """Create mock MenuEngine."""
        engine = Mock()
        engine.generate_slug = Mock(return_value="test-restaurant")
        return engine

    @pytest.fixture
    def mock_theme_engine(self):
        """Create mock ThemeEngine."""
        engine = Mock()
        engine.validate_theme = Mock(return_value=True)
        return engine

    async def test_create_brand_with_valid_data(
        self, mock_brand_repository, mock_menu_engine, mock_theme_engine
    ):
        """Test creating brand with valid data."""
        from src.application.use_cases.create_brand import CreateBrand
        from src.domain.entities.brand import Brand

        # Arrange
        use_case = CreateBrand(
            brand_repository=mock_brand_repository,
            menu_engine=mock_menu_engine,
            theme_engine=mock_theme_engine,
        )

        brand_data = {
            "name": "測試餐廳",
            "slug": "test-restaurant",
            "theme_config": {
                "primaryColor": "#FF6B6B",
                "secondaryColor": "#4ECDC4",
            },
        }

        # Setup mock to return created brand
        created_brand = Brand(**brand_data)
        mock_brand_repository.create.return_value = created_brand

        # Act
        result = await use_case.execute(brand_data)

        # Assert
        assert result.name == "測試餐廳"
        assert result.slug == "test-restaurant"
        mock_brand_repository.exists_by_slug.assert_called_once_with("test-restaurant")
        mock_brand_repository.create.assert_called_once()

    async def test_create_brand_generates_slug_from_name(
        self, mock_brand_repository, mock_menu_engine, mock_theme_engine
    ):
        """Test that slug is auto-generated from name if not provided."""
        from src.application.use_cases.create_brand import CreateBrand
        from src.domain.entities.brand import Brand

        # Arrange
        use_case = CreateBrand(
            brand_repository=mock_brand_repository,
            menu_engine=mock_menu_engine,
            theme_engine=mock_theme_engine,
        )

        brand_data = {
            "name": "測試餐廳",
            # No slug provided
            "theme_config": {"primaryColor": "#FF6B6B"},
        }

        created_brand = Brand(
            name="測試餐廳",
            slug="test-restaurant",
            theme_config={"primaryColor": "#FF6B6B"},
        )
        mock_brand_repository.create.return_value = created_brand

        # Act
        result = await use_case.execute(brand_data)

        # Assert
        mock_menu_engine.generate_slug.assert_called_once_with("測試餐廳")
        assert result.slug == "test-restaurant"

    async def test_create_brand_fails_with_duplicate_slug(
        self, mock_brand_repository, mock_menu_engine, mock_theme_engine
    ):
        """Test that creating brand with duplicate slug fails."""
        from src.application.use_cases.create_brand import CreateBrand
        from src.domain.exceptions import DuplicateSlugError

        # Arrange
        use_case = CreateBrand(
            brand_repository=mock_brand_repository,
            menu_engine=mock_menu_engine,
            theme_engine=mock_theme_engine,
        )

        brand_data = {
            "name": "測試餐廳",
            "slug": "existing-slug",
            "theme_config": {"primaryColor": "#FF6B6B"},
        }

        # Mock slug already exists
        mock_brand_repository.exists_by_slug.return_value = True

        # Act & Assert
        with pytest.raises(DuplicateSlugError):
            await use_case.execute(brand_data)

    async def test_create_brand_validates_theme(
        self, mock_brand_repository, mock_menu_engine, mock_theme_engine
    ):
        """Test that theme configuration is validated."""
        from src.application.use_cases.create_brand import CreateBrand
        from src.domain.entities.brand import Brand

        # Arrange
        use_case = CreateBrand(
            brand_repository=mock_brand_repository,
            menu_engine=mock_menu_engine,
            theme_engine=mock_theme_engine,
        )

        brand_data = {
            "name": "測試餐廳",
            "slug": "test-restaurant",
            "theme_config": {"primaryColor": "#FF6B6B"},
        }

        created_brand = Brand(**brand_data)
        mock_brand_repository.create.return_value = created_brand

        # Act
        await use_case.execute(brand_data)

        # Assert
        mock_theme_engine.validate_theme.assert_called_once()

    async def test_create_brand_with_optional_fields(
        self, mock_brand_repository, mock_menu_engine, mock_theme_engine
    ):
        """Test creating brand with optional fields."""
        from src.application.use_cases.create_brand import CreateBrand
        from src.domain.entities.brand import Brand

        # Arrange
        use_case = CreateBrand(
            brand_repository=mock_brand_repository,
            menu_engine=mock_menu_engine,
            theme_engine=mock_theme_engine,
        )

        brand_data = {
            "name": "測試餐廳",
            "slug": "test-restaurant",
            "description": "這是測試餐廳",
            "logo_url": "https://example.com/logo.png",
            "theme_config": {"primaryColor": "#FF6B6B"},
        }

        created_brand = Brand(**brand_data)
        mock_brand_repository.create.return_value = created_brand

        # Act
        result = await use_case.execute(brand_data)

        # Assert
        assert result.description == "這是測試餐廳"
        assert result.logo_url == "https://example.com/logo.png"
