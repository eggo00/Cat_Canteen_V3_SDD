"""MenuItem entity.

Represents a menu item with customization options.
"""
from uuid import UUID, uuid4

from src.domain.entities.customization_option import CustomizationOption
from src.domain.exceptions import ValidationError


class MenuItem:
    """Menu item entity."""

    def __init__(
        self,
        name: str,
        price: float,
        display_order: int,
        description: str | None = None,
        customization_options: list[CustomizationOption] | None = None,
        id: UUID | None = None,
        is_available: bool = True,
    ) -> None:
        """Initialize menu item.

        Args:
            name: Item name
            price: Item price (must be non-negative)
            display_order: Display order in category
            description: Optional item description
            customization_options: List of customization options
            id: Unique identifier (auto-generated if not provided)
            is_available: Whether item is available for ordering

        Raises:
            ValidationError: If validation fails
        """
        # Validate name
        if not name or not name.strip():
            raise ValidationError("Menu item name cannot be empty")

        if len(name) > 255:
            raise ValidationError(
                f"Menu item name cannot exceed 255 characters (got {len(name)})"
            )

        # Validate price
        if price < 0:
            raise ValidationError(f"Menu item price cannot be negative (got {price})")

        # Set attributes
        self.id = id or uuid4()
        self.name = name
        self.price = price
        self.display_order = display_order
        self.description = description
        self.customization_options = customization_options or []
        self.is_available = is_available

    def add_customization_option(self, option: CustomizationOption) -> None:
        """Add a customization option to the menu item.

        Args:
            option: CustomizationOption to add
        """
        if option not in self.customization_options:
            self.customization_options.append(option)

    def remove_customization_option(self, option: CustomizationOption) -> None:
        """Remove a customization option from the menu item.

        Args:
            option: CustomizationOption to remove
        """
        if option in self.customization_options:
            self.customization_options.remove(option)

    def __eq__(self, other: object) -> bool:
        """Check equality based on ID."""
        if not isinstance(other, MenuItem):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        """Return hash based on ID."""
        return hash(self.id)

    def __repr__(self) -> str:
        """Return string representation."""
        return (
            f"MenuItem(id={self.id}, name='{self.name}', price={self.price}, "
            f"display_order={self.display_order}, "
            f"customization_options={len(self.customization_options)})"
        )
