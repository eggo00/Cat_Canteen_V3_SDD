"""OrderService - Domain Service.

Handles order-related business logic and validation.
"""

from decimal import Decimal
from uuid import UUID

from src.domain.entities.order import Order
from src.domain.entities.order_item import OrderItem
from src.domain.exceptions import ValidationError
from src.domain.value_objects.order_status import OrderStatus


class OrderService:
    """Domain service for order-related operations.

    Handles order validation, total calculation, and business rules.
    """

    # Minimum order amount (can be configurable per brand)
    MIN_ORDER_AMOUNT = Decimal("0")
    # Maximum items per order
    MAX_ITEMS_PER_ORDER = 50

    def validate_order(self, order: Order) -> list[str]:
        """Validate an order for completeness and business rules.

        Args:
            order: Order to validate

        Returns:
            list[str]: List of validation errors (empty if valid)
        """
        errors = []

        # Check if order has items
        if not order.items:
            errors.append("Order must have at least one item")

        # Check maximum items
        if len(order.items) > self.MAX_ITEMS_PER_ORDER:
            errors.append(f"Order cannot have more than {self.MAX_ITEMS_PER_ORDER} items")

        # Check minimum order amount
        if order.total < self.MIN_ORDER_AMOUNT:
            errors.append(f"Order total must be at least {self.MIN_ORDER_AMOUNT}")

        # Validate each item
        for i, item in enumerate(order.items):
            if item.quantity < 1:
                errors.append(f"Item {i + 1}: Quantity must be at least 1")
            if item.unit_price < 0:
                errors.append(f"Item {i + 1}: Price cannot be negative")

        return errors

    def calculate_total(self, items: list[OrderItem]) -> Decimal:
        """Calculate total for a list of order items.

        Args:
            items: List of order items

        Returns:
            Decimal: Total amount
        """
        return sum((item.subtotal for item in items), Decimal("0"))

    def create_order_item(
        self,
        menu_item_id: UUID,
        menu_item_name: str,
        quantity: int,
        unit_price: Decimal | float,
        customizations: list[dict] | None = None,
        notes: str | None = None,
    ) -> OrderItem:
        """Create a validated order item.

        Args:
            menu_item_id: Menu item reference
            menu_item_name: Menu item name
            quantity: Quantity to order
            unit_price: Price per unit
            customizations: Selected customizations
            notes: Special instructions

        Returns:
            OrderItem: Created order item

        Raises:
            ValidationError: If validation fails
        """
        return OrderItem(
            menu_item_id=menu_item_id,
            menu_item_name=menu_item_name,
            quantity=quantity,
            unit_price=unit_price,
            customizations=customizations,
            notes=notes,
        )

    def can_cancel_order(self, order: Order) -> bool:
        """Check if an order can be cancelled.

        Args:
            order: Order to check

        Returns:
            bool: True if order can be cancelled
        """
        # Can cancel if not already in final state
        return not order.status.is_final

    def can_modify_order(self, order: Order) -> bool:
        """Check if an order can be modified.

        Args:
            order: Order to check

        Returns:
            bool: True if order can be modified
        """
        # Can only modify pending orders
        return order.status == OrderStatus.PENDING

    def get_next_statuses(self, current_status: OrderStatus) -> list[OrderStatus]:
        """Get list of valid next statuses.

        Args:
            current_status: Current order status

        Returns:
            list[OrderStatus]: Valid next statuses
        """
        transitions = {
            OrderStatus.PENDING: [OrderStatus.CONFIRMED, OrderStatus.CANCELLED],
            OrderStatus.CONFIRMED: [OrderStatus.PREPARING, OrderStatus.CANCELLED],
            OrderStatus.PREPARING: [OrderStatus.READY, OrderStatus.CANCELLED],
            OrderStatus.READY: [OrderStatus.COMPLETED, OrderStatus.CANCELLED],
            OrderStatus.COMPLETED: [],
            OrderStatus.CANCELLED: [],
        }
        return transitions.get(current_status, [])

    def estimate_preparation_time(self, order: Order) -> int:
        """Estimate preparation time in minutes.

        Simple estimation based on number of items.
        Can be enhanced with more sophisticated logic.

        Args:
            order: Order to estimate

        Returns:
            int: Estimated minutes
        """
        base_time = 5  # Base preparation time
        per_item_time = 2  # Additional time per item

        return base_time + (order.item_count * per_item_time)

    def format_order_summary(self, order: Order) -> str:
        """Format order summary for display or notification.

        Args:
            order: Order to format

        Returns:
            str: Formatted summary
        """
        lines = [
            f"訂單編號: {order.order_number}",
            f"顧客: {order.customer_name}",
            f"電話: {order.customer_phone}",
            f"狀態: {order.status.display_name}",
            "",
            "品項:",
        ]

        for item in order.items:
            customization_text = ""
            if item.customizations:
                custom_names = [c.get("name", "") for c in item.customizations]
                customization_text = f" ({', '.join(custom_names)})"

            lines.append(
                f"  - {item.menu_item_name} x{item.quantity} "
                f"NT${item.subtotal:.0f}{customization_text}"
            )

        if order.notes:
            lines.extend(["", f"備註: {order.notes}"])

        lines.extend(["", f"總計: NT${order.total:.0f}"])

        return "\n".join(lines)
