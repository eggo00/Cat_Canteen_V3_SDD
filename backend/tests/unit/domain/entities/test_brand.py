"""Unit tests for Brand entity.

Tests the Brand domain entity business logic and validation rules.
"""
import pytest
from uuid import UUID


class TestBrandEntity:
    """Test Brand entity validation and business logic."""

    def test_create_brand_with_valid_data(self, sample_brand_data):
        """Test creating a brand with valid data."""
        from src.domain.entities.brand import Brand

        # Act
        brand = Brand(**sample_brand_data)

        # Assert
        assert brand.name == "測試餐廳"
        assert brand.slug == "test-restaurant"
        assert brand.is_active is True
        assert brand.theme_config.primary_color == "#FF6B6B"

    def test_brand_slug_must_be_lowercase(self):
        """Test that brand slug is automatically converted to lowercase."""
        from src.domain.entities.brand import Brand

        # Arrange
        data = {
            "name": "Test Brand",
            "slug": "Test-BRAND",  # Mixed case
            "theme_config": {"primaryColor": "#000000"},
        }

        # Act
        brand = Brand(**data)

        # Assert
        assert brand.slug == "test-brand"

    def test_brand_slug_validates_format(self):
        """Test that brand slug only allows valid URL-safe characters."""
        from src.domain.entities.brand import Brand, InvalidSlugError

        # Arrange - Invalid characters
        data = {
            "name": "Test Brand",
            "slug": "test brand!@#",  # Spaces and special chars
            "theme_config": {"primaryColor": "#000000"},
        }

        # Act & Assert
        with pytest.raises(InvalidSlugError):
            Brand(**data)

    def test_brand_requires_name(self):
        """Test that brand name is required."""
        from src.domain.entities.brand import Brand

        # Arrange
        data = {
            "slug": "test-brand",
            "theme_config": {"primaryColor": "#000000"},
        }

        # Act & Assert
        with pytest.raises(TypeError):
            Brand(**data)  # type: ignore

    def test_brand_requires_theme_config(self):
        """Test that theme_config is required."""
        from src.domain.entities.brand import Brand

        # Arrange
        data = {
            "name": "Test Brand",
            "slug": "test-brand",
        }

        # Act & Assert
        with pytest.raises(TypeError):
            Brand(**data)  # type: ignore

    def test_brand_name_max_length(self):
        """Test that brand name has maximum length."""
        from src.domain.entities.brand import Brand, ValidationError

        # Arrange - Name too long (> 255 characters)
        data = {
            "name": "A" * 300,
            "slug": "test-brand",
            "theme_config": {"primaryColor": "#000000"},
        }

        # Act & Assert
        with pytest.raises(ValidationError):
            Brand(**data)

    def test_brand_slug_max_length(self):
        """Test that brand slug has maximum length."""
        from src.domain.entities.brand import Brand, ValidationError

        # Arrange - Slug too long (> 255 characters)
        data = {
            "name": "Test Brand",
            "slug": "a" * 300,
            "theme_config": {"primaryColor": "#000000"},
        }

        # Act & Assert
        with pytest.raises(ValidationError):
            Brand(**data)

    def test_brand_can_be_deactivated(self, sample_brand_data):
        """Test that brand can be deactivated."""
        from src.domain.entities.brand import Brand

        # Arrange
        brand = Brand(**sample_brand_data)

        # Act
        brand.deactivate()

        # Assert
        assert brand.is_active is False

    def test_brand_can_be_reactivated(self, sample_brand_data):
        """Test that brand can be reactivated."""
        from src.domain.entities.brand import Brand

        # Arrange
        brand = Brand(**sample_brand_data)
        brand.deactivate()

        # Act
        brand.activate()

        # Assert
        assert brand.is_active is True

    def test_brand_theme_can_be_updated(self, sample_brand_data):
        """Test that brand theme can be updated."""
        from src.domain.entities.brand import Brand

        # Arrange
        brand = Brand(**sample_brand_data)
        new_theme = {
            "primaryColor": "#000000",
            "secondaryColor": "#FFFFFF",
        }

        # Act
        brand.update_theme(new_theme)

        # Assert
        assert brand.theme_config.primary_color == "#000000"
        assert brand.theme_config.secondary_color == "#FFFFFF"
