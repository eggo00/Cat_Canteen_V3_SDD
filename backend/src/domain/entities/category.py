"""Category entity.

Represents a menu category containing menu items.
"""
from uuid import UUID, uuid4

from src.domain.entities.menu_item import MenuItem
from src.domain.exceptions import ValidationError


class Category:
    """Menu category entity."""

    def __init__(
        self,
        name: str,
        display_order: int,
        description: str | None = None,
        menu_items: list[MenuItem] | None = None,
        id: UUID | None = None,
    ) -> None:
        """Initialize category.

        Args:
            name: Category name
            display_order: Display order in menu
            description: Optional category description
            menu_items: List of menu items in this category
            id: Unique identifier (auto-generated if not provided)

        Raises:
            ValidationError: If validation fails
        """
        # Validate name
        if not name or not name.strip():
            raise ValidationError("Category name cannot be empty")

        if len(name) > 255:
            raise ValidationError(
                f"Category name cannot exceed 255 characters (got {len(name)})"
            )

        # Set attributes
        self.id = id or uuid4()
        self.name = name
        self.display_order = display_order
        self.description = description
        self.menu_items = menu_items or []

    def add_menu_item(self, item: MenuItem) -> None:
        """Add a menu item to the category.

        Args:
            item: MenuItem to add
        """
        if item not in self.menu_items:
            self.menu_items.append(item)

    def remove_menu_item(self, item: MenuItem) -> None:
        """Remove a menu item from the category.

        Args:
            item: MenuItem to remove
        """
        if item in self.menu_items:
            self.menu_items.remove(item)

    def reorder_menu_items(self, items: list[MenuItem]) -> None:
        """Reorder menu items in the category.

        Args:
            items: New order of menu items

        Raises:
            ValidationError: If items list doesn't match current items
        """
        # Validate that the items list contains the same items (just reordered)
        if set(items) != set(self.menu_items):
            raise ValidationError("Reorder items must match current menu items")

        self.menu_items = items

    def __eq__(self, other: object) -> bool:
        """Check equality based on ID."""
        if not isinstance(other, Category):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        """Return hash based on ID."""
        return hash(self.id)

    def __repr__(self) -> str:
        """Return string representation."""
        return (
            f"Category(id={self.id}, name='{self.name}', "
            f"display_order={self.display_order}, "
            f"menu_items={len(self.menu_items)})"
        )
