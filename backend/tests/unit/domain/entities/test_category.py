"""Unit tests for Category entity.

Tests category validation and business logic.
"""
import pytest


class TestCategory:
    """Test Category entity."""

    def test_create_category_with_valid_data(self):
        """Test creating category with valid data."""
        from src.domain.entities.category import Category

        # Arrange & Act
        category = Category(
            name="飲料",
            description="各式飲品",
            display_order=1,
        )

        # Assert
        assert category.name == "飲料"
        assert category.description == "各式飲品"
        assert category.display_order == 1
        assert category.menu_items == []

    def test_category_with_menu_items(self):
        """Test category with menu items."""
        from src.domain.entities.category import Category
        from src.domain.entities.menu_item import MenuItem

        # Arrange
        items = [
            MenuItem(name="美式咖啡", price=100.00, display_order=1),
            MenuItem(name="拿鐵咖啡", price=120.00, display_order=2),
        ]

        # Act
        category = Category(
            name="飲料",
            description="各式飲品",
            display_order=1,
            menu_items=items,
        )

        # Assert
        assert len(category.menu_items) == 2
        assert category.menu_items[0].name == "美式咖啡"
        assert category.menu_items[1].name == "拿鐵咖啡"

    def test_category_requires_name(self):
        """Test that name is required."""
        from src.domain.entities.category import Category

        with pytest.raises(TypeError):
            Category(  # type: ignore
                description="各式飲品",
                display_order=1,
            )

    def test_category_name_cannot_be_empty(self):
        """Test that name cannot be empty string."""
        from src.domain.entities.category import Category, ValidationError

        with pytest.raises(ValidationError):
            Category(
                name="",
                description="各式飲品",
                display_order=1,
            )

    def test_category_name_max_length(self):
        """Test that name has maximum length of 255."""
        from src.domain.entities.category import Category, ValidationError

        with pytest.raises(ValidationError):
            Category(
                name="A" * 256,  # Exceeds 255 characters
                description="各式飲品",
                display_order=1,
            )

    def test_category_description_is_optional(self):
        """Test that description is optional."""
        from src.domain.entities.category import Category

        category = Category(
            name="飲料",
            display_order=1,
        )

        assert category.description is None

    def test_category_can_add_menu_item(self):
        """Test adding menu item to category."""
        from src.domain.entities.category import Category
        from src.domain.entities.menu_item import MenuItem

        # Arrange
        category = Category(
            name="飲料",
            display_order=1,
        )
        item = MenuItem(name="美式咖啡", price=100.00, display_order=1)

        # Act
        category.add_menu_item(item)

        # Assert
        assert len(category.menu_items) == 1
        assert category.menu_items[0].name == "美式咖啡"

    def test_category_can_remove_menu_item(self):
        """Test removing menu item from category."""
        from src.domain.entities.category import Category
        from src.domain.entities.menu_item import MenuItem

        # Arrange
        item = MenuItem(name="美式咖啡", price=100.00, display_order=1)
        category = Category(
            name="飲料",
            display_order=1,
            menu_items=[item],
        )

        # Act
        category.remove_menu_item(item)

        # Assert
        assert len(category.menu_items) == 0

    def test_category_can_reorder_menu_items(self):
        """Test reordering menu items in category."""
        from src.domain.entities.category import Category
        from src.domain.entities.menu_item import MenuItem

        # Arrange
        item1 = MenuItem(name="美式咖啡", price=100.00, display_order=1)
        item2 = MenuItem(name="拿鐵咖啡", price=120.00, display_order=2)
        category = Category(
            name="飲料",
            display_order=1,
            menu_items=[item1, item2],
        )

        # Act
        category.reorder_menu_items([item2, item1])

        # Assert
        assert category.menu_items[0].name == "拿鐵咖啡"
        assert category.menu_items[1].name == "美式咖啡"
