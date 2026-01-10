"""Unit tests for MenuItem entity.

Tests menu item validation and business logic.
"""
import pytest


class TestMenuItem:
    """Test MenuItem entity."""

    def test_create_menu_item_with_valid_data(self):
        """Test creating menu item with valid data."""
        from src.domain.entities.menu_item import MenuItem

        # Arrange & Act
        item = MenuItem(
            name="美式咖啡",
            description="香醇美式咖啡",
            price=100.00,
            display_order=1,
        )

        # Assert
        assert item.name == "美式咖啡"
        assert item.description == "香醇美式咖啡"
        assert item.price == 100.00
        assert item.display_order == 1
        assert item.customization_options == []

    def test_menu_item_with_customization_options(self):
        """Test menu item with customization options."""
        from src.domain.entities.customization_option import CustomizationOption
        from src.domain.entities.menu_item import MenuItem

        # Arrange
        options = [
            CustomizationOption(
                option_type="size",
                name="大杯",
                price_adjustment=20.00,
            ),
            CustomizationOption(
                option_type="sweetness",
                name="半糖",
                price_adjustment=0.00,
            ),
        ]

        # Act
        item = MenuItem(
            name="美式咖啡",
            price=100.00,
            display_order=1,
            customization_options=options,
        )

        # Assert
        assert len(item.customization_options) == 2
        assert item.customization_options[0].name == "大杯"
        assert item.customization_options[1].name == "半糖"

    def test_menu_item_requires_name(self):
        """Test that name is required."""
        from src.domain.entities.menu_item import MenuItem

        with pytest.raises(TypeError):
            MenuItem(  # type: ignore
                price=100.00,
                display_order=1,
            )

    def test_menu_item_requires_price(self):
        """Test that price is required."""
        from src.domain.entities.menu_item import MenuItem

        with pytest.raises(TypeError):
            MenuItem(  # type: ignore
                name="美式咖啡",
                display_order=1,
            )

    def test_menu_item_price_must_be_non_negative(self):
        """Test that price cannot be negative."""
        from src.domain.entities.menu_item import MenuItem, ValidationError

        with pytest.raises(ValidationError):
            MenuItem(
                name="美式咖啡",
                price=-10.00,
                display_order=1,
            )

    def test_menu_item_name_cannot_be_empty(self):
        """Test that name cannot be empty string."""
        from src.domain.entities.menu_item import MenuItem, ValidationError

        with pytest.raises(ValidationError):
            MenuItem(
                name="",
                price=100.00,
                display_order=1,
            )

    def test_menu_item_name_max_length(self):
        """Test that name has maximum length of 255."""
        from src.domain.entities.menu_item import MenuItem, ValidationError

        with pytest.raises(ValidationError):
            MenuItem(
                name="A" * 256,  # Exceeds 255 characters
                price=100.00,
                display_order=1,
            )

    def test_menu_item_description_is_optional(self):
        """Test that description is optional."""
        from src.domain.entities.menu_item import MenuItem

        item = MenuItem(
            name="美式咖啡",
            price=100.00,
            display_order=1,
        )

        assert item.description is None

    def test_menu_item_can_add_customization_option(self):
        """Test adding customization option to menu item."""
        from src.domain.entities.customization_option import CustomizationOption
        from src.domain.entities.menu_item import MenuItem

        # Arrange
        item = MenuItem(
            name="美式咖啡",
            price=100.00,
            display_order=1,
        )
        option = CustomizationOption(
            option_type="size",
            name="大杯",
            price_adjustment=20.00,
        )

        # Act
        item.add_customization_option(option)

        # Assert
        assert len(item.customization_options) == 1
        assert item.customization_options[0].name == "大杯"

    def test_menu_item_can_remove_customization_option(self):
        """Test removing customization option from menu item."""
        from src.domain.entities.customization_option import CustomizationOption
        from src.domain.entities.menu_item import MenuItem

        # Arrange
        option = CustomizationOption(
            option_type="size",
            name="大杯",
            price_adjustment=20.00,
        )
        item = MenuItem(
            name="美式咖啡",
            price=100.00,
            display_order=1,
            customization_options=[option],
        )

        # Act
        item.remove_customization_option(option)

        # Assert
        assert len(item.customization_options) == 0
