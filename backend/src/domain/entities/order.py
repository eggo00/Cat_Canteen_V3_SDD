"""Order Entity - Domain Model.

Represents a customer order in the ordering system.
"""

import re
from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4

from src.domain.entities.order_item import OrderItem
from src.domain.exceptions import ValidationError
from src.domain.value_objects.order_status import OrderStatus


class Order:
    """Order entity representing a customer order.

    An order contains items, customer information, and tracks
    the order lifecycle through various statuses.
    """

    def __init__(
        self,
        brand_id: UUID,
        customer_name: str,
        customer_phone: str,
        id: UUID | None = None,
        order_number: str | None = None,
        items: list[OrderItem] | None = None,
        status: OrderStatus | str = OrderStatus.PENDING,
        notes: str | None = None,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ):
        """Initialize an Order entity.

        Args:
            brand_id: Reference to the brand
            customer_name: Customer name (required)
            customer_phone: Customer phone number (required, Taiwan format)
            id: Unique identifier (auto-generated if not provided)
            order_number: Human-readable order number (auto-generated if not provided)
            items: List of order items
            status: Order status (default: PENDING)
            notes: Order-level notes or special instructions
            created_at: Creation timestamp
            updated_at: Last update timestamp

        Raises:
            ValidationError: If validation fails
        """
        # Validate required fields
        if not brand_id:
            raise ValidationError("Brand ID is required")

        if not customer_name or not customer_name.strip():
            raise ValidationError("Customer name is required")

        if not customer_phone or not customer_phone.strip():
            raise ValidationError("Customer phone is required")

        # Validate phone format (Taiwan mobile: 09XX-XXX-XXX or 09XXXXXXXX)
        normalized_phone = self._validate_and_normalize_phone(customer_phone)

        # Convert status string to enum if needed
        if isinstance(status, str):
            status = OrderStatus.from_string(status)

        # Set attributes
        self.id = id or uuid4()
        self.brand_id = brand_id
        self.order_number = order_number or self._generate_order_number()
        self.customer_name = customer_name.strip()
        self.customer_phone = normalized_phone
        self.items = items or []
        self.status = status
        self.notes = notes
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

        # Set order_id on all items
        for item in self.items:
            item.order_id = self.id

    @staticmethod
    def _validate_and_normalize_phone(phone: str) -> str:
        """Validate and normalize phone number.

        Accepts Taiwan mobile phone formats:
        - 0912345678
        - 0912-345-678
        - 09-1234-5678

        Args:
            phone: Phone number to validate

        Returns:
            str: Normalized phone number (digits only)

        Raises:
            ValidationError: If phone format is invalid
        """
        # Remove spaces, dashes, and other separators
        digits_only = re.sub(r"[\s\-\(\)]+", "", phone)

        # Taiwan mobile phone pattern: 09XXXXXXXX (10 digits starting with 09)
        if not re.match(r"^09\d{8}$", digits_only):
            raise ValidationError(
                f"Invalid phone format: '{phone}'. "
                "Please use Taiwan mobile format (e.g., 0912345678)"
            )

        return digits_only

    @staticmethod
    def _generate_order_number() -> str:
        """Generate a human-readable order number.

        Format: YYYYMMDD-XXXX (date + 4 random chars)

        Returns:
            str: Generated order number
        """
        import random
        import string

        date_part = datetime.utcnow().strftime("%Y%m%d")
        random_part = "".join(random.choices(string.ascii_uppercase + string.digits, k=4))
        return f"{date_part}-{random_part}"

    @property
    def total(self) -> Decimal:
        """Calculate total order amount.

        Returns:
            Decimal: Sum of all item subtotals
        """
        return sum((item.subtotal for item in self.items), Decimal("0"))

    @property
    def item_count(self) -> int:
        """Get total number of items (including quantities).

        Returns:
            int: Total item count
        """
        return sum(item.quantity for item in self.items)

    def add_item(self, item: OrderItem) -> None:
        """Add an item to the order.

        Args:
            item: OrderItem to add

        Raises:
            ValidationError: If order is in final state
        """
        if self.status.is_final:
            raise ValidationError(f"Cannot add items to {self.status.value} order")

        item.order_id = self.id
        self.items.append(item)
        self._touch()

    def remove_item(self, item_id: UUID) -> bool:
        """Remove an item from the order.

        Args:
            item_id: ID of item to remove

        Returns:
            bool: True if item was removed

        Raises:
            ValidationError: If order is in final state
        """
        if self.status.is_final:
            raise ValidationError(f"Cannot remove items from {self.status.value} order")

        original_count = len(self.items)
        self.items = [item for item in self.items if item.id != item_id]
        removed = len(self.items) < original_count

        if removed:
            self._touch()

        return removed

    def update_status(self, new_status: OrderStatus | str) -> None:
        """Update order status.

        Args:
            new_status: New status to transition to

        Raises:
            ValidationError: If transition is not allowed
        """
        if isinstance(new_status, str):
            new_status = OrderStatus.from_string(new_status)

        if not self.status.can_transition_to(new_status):
            raise ValidationError(
                f"Cannot transition from {self.status.value} to {new_status.value}"
            )

        self.status = new_status
        self._touch()

    def confirm(self) -> None:
        """Confirm the order."""
        self.update_status(OrderStatus.CONFIRMED)

    def start_preparing(self) -> None:
        """Mark order as being prepared."""
        self.update_status(OrderStatus.PREPARING)

    def mark_ready(self) -> None:
        """Mark order as ready for pickup."""
        self.update_status(OrderStatus.READY)

    def complete(self) -> None:
        """Mark order as completed."""
        self.update_status(OrderStatus.COMPLETED)

    def cancel(self) -> None:
        """Cancel the order."""
        if self.status.is_final:
            raise ValidationError(f"Cannot cancel {self.status.value} order")
        self.status = OrderStatus.CANCELLED
        self._touch()

    def _touch(self) -> None:
        """Update the updated_at timestamp."""
        self.updated_at = datetime.utcnow()

    def to_dict(self) -> dict:
        """Convert to dictionary representation.

        Returns:
            dict: Dictionary with all order data
        """
        return {
            "id": str(self.id),
            "brand_id": str(self.brand_id),
            "order_number": self.order_number,
            "customer_name": self.customer_name,
            "customer_phone": self.customer_phone,
            "items": [item.to_dict() for item in self.items],
            "status": self.status.value,
            "status_display": self.status.display_name,
            "notes": self.notes,
            "total": float(self.total),
            "item_count": self.item_count,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self) -> str:
        """String representation of Order."""
        return (
            f"<Order(id={self.id}, number={self.order_number}, "
            f"status={self.status.value}, total={self.total})>"
        )

    def __eq__(self, other: object) -> bool:
        """Compare two orders for equality (by ID).

        Args:
            other: Other object to compare

        Returns:
            bool: True if IDs are equal
        """
        if not isinstance(other, Order):
            return False
        return self.id == other.id
