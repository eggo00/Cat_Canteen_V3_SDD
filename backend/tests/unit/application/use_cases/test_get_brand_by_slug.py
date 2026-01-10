"""Unit tests for GetBrandBySlug use case.

Tests retrieving brand by slug.
"""
import pytest
from unittest.mock import AsyncMock


class TestGetBrandBySlug:
    """Test GetBrandBySlug use case."""

    @pytest.fixture
    def mock_brand_repository(self):
        """Create mock BrandRepository."""
        repository = AsyncMock()
        repository.get_by_slug = AsyncMock()
        return repository

    async def test_get_brand_by_slug_success(self, mock_brand_repository):
        """Test successfully retrieving brand by slug."""
        from src.application.use_cases.get_brand_by_slug import GetBrandBySlug
        from src.domain.entities.brand import Brand

        # Arrange
        use_case = GetBrandBySlug(brand_repository=mock_brand_repository)

        brand = Brand(
            name="測試餐廳",
            slug="test-restaurant",
            theme_config={"primaryColor": "#FF6B6B"},
        )
        mock_brand_repository.get_by_slug.return_value = brand

        # Act
        result = await use_case.execute("test-restaurant")

        # Assert
        assert result is not None
        assert result.slug == "test-restaurant"
        assert result.name == "測試餐廳"
        mock_brand_repository.get_by_slug.assert_called_once_with("test-restaurant")

    async def test_get_brand_by_slug_not_found(self, mock_brand_repository):
        """Test retrieving non-existent brand returns None."""
        from src.application.use_cases.get_brand_by_slug import GetBrandBySlug

        # Arrange
        use_case = GetBrandBySlug(brand_repository=mock_brand_repository)
        mock_brand_repository.get_by_slug.return_value = None

        # Act
        result = await use_case.execute("non-existent-slug")

        # Assert
        assert result is None
        mock_brand_repository.get_by_slug.assert_called_once_with("non-existent-slug")

    async def test_get_brand_by_slug_with_inactive_brand(self, mock_brand_repository):
        """Test can retrieve inactive brand."""
        from src.application.use_cases.get_brand_by_slug import GetBrandBySlug
        from src.domain.entities.brand import Brand

        # Arrange
        use_case = GetBrandBySlug(brand_repository=mock_brand_repository)

        brand = Brand(
            name="測試餐廳",
            slug="test-restaurant",
            theme_config={"primaryColor": "#FF6B6B"},
            is_active=False,
        )
        mock_brand_repository.get_by_slug.return_value = brand

        # Act
        result = await use_case.execute("test-restaurant")

        # Assert
        assert result is not None
        assert result.is_active is False
