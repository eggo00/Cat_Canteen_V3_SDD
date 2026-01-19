"""OrderStatus Value Object - Domain Model.

Represents the status of an order in the ordering system.
"""

from enum import Enum


class OrderStatus(str, Enum):
    """Order status enumeration.

    Represents the lifecycle states of an order:
    - PENDING: Order has been placed, awaiting confirmation
    - CONFIRMED: Order has been confirmed by the restaurant
    - PREPARING: Order is being prepared
    - READY: Order is ready for pickup/delivery
    - COMPLETED: Order has been completed (picked up/delivered)
    - CANCELLED: Order has been cancelled
    """

    PENDING = "pending"
    CONFIRMED = "confirmed"
    PREPARING = "preparing"
    READY = "ready"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

    @classmethod
    def from_string(cls, value: str) -> "OrderStatus":
        """Create OrderStatus from string value.

        Args:
            value: Status string (case-insensitive)

        Returns:
            OrderStatus: Corresponding enum value

        Raises:
            ValueError: If value is not a valid status
        """
        normalized = value.lower().strip()
        for status in cls:
            if status.value == normalized:
                return status
        raise ValueError(
            f"Invalid order status: '{value}'. "
            f"Valid statuses are: {', '.join(s.value for s in cls)}"
        )

    def can_transition_to(self, new_status: "OrderStatus") -> bool:
        """Check if transition to new status is allowed.

        Args:
            new_status: Target status

        Returns:
            bool: True if transition is allowed
        """
        # Define valid state transitions
        valid_transitions = {
            OrderStatus.PENDING: {OrderStatus.CONFIRMED, OrderStatus.CANCELLED},
            OrderStatus.CONFIRMED: {OrderStatus.PREPARING, OrderStatus.CANCELLED},
            OrderStatus.PREPARING: {OrderStatus.READY, OrderStatus.CANCELLED},
            OrderStatus.READY: {OrderStatus.COMPLETED, OrderStatus.CANCELLED},
            OrderStatus.COMPLETED: set(),  # Final state
            OrderStatus.CANCELLED: set(),  # Final state
        }
        return new_status in valid_transitions.get(self, set())

    @property
    def is_final(self) -> bool:
        """Check if this is a final (terminal) status.

        Returns:
            bool: True if status is final
        """
        return self in {OrderStatus.COMPLETED, OrderStatus.CANCELLED}

    @property
    def is_active(self) -> bool:
        """Check if order is still active (not final).

        Returns:
            bool: True if order is still in progress
        """
        return not self.is_final

    @property
    def display_name(self) -> str:
        """Get human-readable display name.

        Returns:
            str: Display name in Chinese
        """
        names = {
            OrderStatus.PENDING: "待確認",
            OrderStatus.CONFIRMED: "已確認",
            OrderStatus.PREPARING: "製作中",
            OrderStatus.READY: "已完成",
            OrderStatus.COMPLETED: "已取餐",
            OrderStatus.CANCELLED: "已取消",
        }
        return names.get(self, self.value)
