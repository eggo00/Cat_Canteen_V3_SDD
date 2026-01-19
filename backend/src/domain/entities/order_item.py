"""OrderItem Entity - Domain Model.

Represents an item within an order.
"""

from decimal import Decimal
from uuid import UUID, uuid4

from src.domain.exceptions import ValidationError


class OrderItem:
    """OrderItem entity representing a single item in an order.

    An order item captures what was ordered, including quantity,
    customizations, and the price at the time of order.
    """

    def __init__(
        self,
        menu_item_id: UUID,
        menu_item_name: str,
        quantity: int,
        unit_price: Decimal | float,
        id: UUID | None = None,
        order_id: UUID | None = None,
        customizations: list[dict] | None = None,
        notes: str | None = None,
    ):
        """Initialize an OrderItem entity.

        Args:
            menu_item_id: Reference to the menu item
            menu_item_name: Name of the menu item (snapshot at order time)
            quantity: Number of items ordered (must be positive)
            unit_price: Price per unit at order time
            id: Unique identifier (auto-generated if not provided)
            order_id: Reference to parent order
            customizations: List of customization selections
            notes: Special instructions or notes

        Raises:
            ValidationError: If validation fails
        """
        # Validate required fields
        if not menu_item_id:
            raise ValidationError("Menu item ID is required")

        if not menu_item_name or not menu_item_name.strip():
            raise ValidationError("Menu item name is required")

        if quantity is None or quantity < 1:
            raise ValidationError("Quantity must be at least 1")

        if unit_price is None:
            raise ValidationError("Unit price is required")

        # Convert to Decimal for precision
        if isinstance(unit_price, float):
            unit_price = Decimal(str(unit_price))

        if unit_price < 0:
            raise ValidationError("Unit price cannot be negative")

        # Set attributes
        self.id = id or uuid4()
        self.order_id = order_id
        self.menu_item_id = menu_item_id
        self.menu_item_name = menu_item_name.strip()
        self.quantity = quantity
        self.unit_price = unit_price
        self.customizations = customizations or []
        self.notes = notes

    @property
    def subtotal(self) -> Decimal:
        """Calculate subtotal for this item.

        Returns:
            Decimal: quantity * unit_price + customization adjustments
        """
        base_total = self.unit_price * self.quantity

        # Add customization price adjustments
        customization_total = Decimal("0")
        for customization in self.customizations:
            adjustment = customization.get("price_adjustment", 0)
            if adjustment:
                customization_total += Decimal(str(adjustment)) * self.quantity

        return base_total + customization_total

    def update_quantity(self, quantity: int) -> None:
        """Update item quantity.

        Args:
            quantity: New quantity (must be positive)

        Raises:
            ValidationError: If quantity is invalid
        """
        if quantity < 1:
            raise ValidationError("Quantity must be at least 1")
        self.quantity = quantity

    def add_customization(self, customization: dict) -> None:
        """Add a customization to this item.

        Args:
            customization: Customization data with option_id, name, price_adjustment
        """
        self.customizations.append(customization)

    def clear_customizations(self) -> None:
        """Remove all customizations from this item."""
        self.customizations = []

    def to_dict(self) -> dict:
        """Convert to dictionary representation.

        Returns:
            dict: Dictionary with all item data
        """
        return {
            "id": str(self.id),
            "order_id": str(self.order_id) if self.order_id else None,
            "menu_item_id": str(self.menu_item_id),
            "menu_item_name": self.menu_item_name,
            "quantity": self.quantity,
            "unit_price": float(self.unit_price),
            "subtotal": float(self.subtotal),
            "customizations": self.customizations,
            "notes": self.notes,
        }

    def __repr__(self) -> str:
        """String representation of OrderItem."""
        return (
            f"<OrderItem(id={self.id}, name={self.menu_item_name}, "
            f"qty={self.quantity}, price={self.unit_price})>"
        )

    def __eq__(self, other: object) -> bool:
        """Compare two order items for equality (by ID).

        Args:
            other: Other object to compare

        Returns:
            bool: True if IDs are equal
        """
        if not isinstance(other, OrderItem):
            return False
        return self.id == other.id
