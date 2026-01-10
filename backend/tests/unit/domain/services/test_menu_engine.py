"""Unit tests for MenuEngine domain service.

Tests menu JSON validation and slug generation logic.

⚠️ TDD: These tests should FAIL initially until MenuEngine is implemented.
"""
import pytest


@pytest.mark.skip(reason="MenuEngine not yet implemented")
class TestMenuEngine:
    """Test MenuEngine domain service."""

    def test_validate_menu_json_success(self, sample_menu_data):
        """Test validating correct menu JSON format."""
        from src.domain.services.menu_engine import MenuEngine

        engine = MenuEngine()
        result = engine.validate_menu_json(sample_menu_data)

        assert result is True

    def test_validate_menu_json_missing_categories(self):
        """Test validation fails when categories missing."""
        from src.domain.services.menu_engine import MenuEngine, ValidationError

        engine = MenuEngine()

        with pytest.raises(ValidationError):
            engine.validate_menu_json({})

    def test_generate_slug_from_name(self):
        """Test generating URL-safe slug from name."""
        from src.domain.services.menu_engine import MenuEngine

        engine = MenuEngine()
        slug = engine.generate_slug("測試 餐廳 & Café")

        assert slug == "ce-shi-can-ting-cafe"
        assert " " not in slug
        assert "&" not in slug
