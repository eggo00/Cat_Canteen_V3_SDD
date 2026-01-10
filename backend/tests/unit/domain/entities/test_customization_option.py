"""Unit tests for CustomizationOption entity.

Tests customization option validation and business logic.
"""
import pytest


class TestCustomizationOption:
    """Test CustomizationOption entity."""

    def test_create_customization_option_with_valid_data(self):
        """Test creating customization option with valid data."""
        from src.domain.entities.customization_option import CustomizationOption

        # Arrange & Act
        option = CustomizationOption(
            option_type="size",
            name="大杯",
            price_adjustment=20.00,
        )

        # Assert
        assert option.option_type == "size"
        assert option.name == "大杯"
        assert option.price_adjustment == 20.00

    def test_customization_option_price_adjustment_can_be_zero(self):
        """Test that price adjustment can be zero."""
        from src.domain.entities.customization_option import CustomizationOption

        option = CustomizationOption(
            option_type="sweetness",
            name="半糖",
            price_adjustment=0.00,
        )

        assert option.price_adjustment == 0.00

    def test_customization_option_price_adjustment_can_be_negative(self):
        """Test that price adjustment can be negative (discount)."""
        from src.domain.entities.customization_option import CustomizationOption

        option = CustomizationOption(
            option_type="discount",
            name="會員優惠",
            price_adjustment=-10.00,
        )

        assert option.price_adjustment == -10.00

    def test_customization_option_requires_option_type(self):
        """Test that option_type is required."""
        from src.domain.entities.customization_option import CustomizationOption

        with pytest.raises(TypeError):
            CustomizationOption(  # type: ignore
                name="大杯",
                price_adjustment=20.00,
            )

    def test_customization_option_requires_name(self):
        """Test that name is required."""
        from src.domain.entities.customization_option import CustomizationOption

        with pytest.raises(TypeError):
            CustomizationOption(  # type: ignore
                option_type="size",
                price_adjustment=20.00,
            )

    def test_customization_option_name_cannot_be_empty(self):
        """Test that name cannot be empty string."""
        from src.domain.entities.customization_option import (
            CustomizationOption,
            ValidationError,
        )

        with pytest.raises(ValidationError):
            CustomizationOption(
                option_type="size",
                name="",
                price_adjustment=20.00,
            )

    def test_customization_option_name_max_length(self):
        """Test that name has maximum length of 100."""
        from src.domain.entities.customization_option import (
            CustomizationOption,
            ValidationError,
        )

        with pytest.raises(ValidationError):
            CustomizationOption(
                option_type="size",
                name="A" * 101,  # Exceeds 100 characters
                price_adjustment=20.00,
            )
