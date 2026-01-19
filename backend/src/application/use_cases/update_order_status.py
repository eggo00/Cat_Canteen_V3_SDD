"""UpdateOrderStatus Use Case - Application Layer.

Handles updating order status.
"""

from uuid import UUID

from src.domain.entities.order import Order
from src.domain.exceptions import NotFoundError, ValidationError
from src.domain.repositories.order_repository import OrderRepository
from src.domain.value_objects.order_status import OrderStatus


class UpdateOrderStatus:
    """Use case for updating order status."""

    def __init__(self, order_repository: OrderRepository):
        """Initialize the use case.

        Args:
            order_repository: Repository for order data
        """
        self.order_repository = order_repository

    async def execute(
        self,
        order_id: UUID,
        new_status: OrderStatus | str,
    ) -> Order:
        """Update order status.

        Args:
            order_id: Order UUID
            new_status: New status to set

        Returns:
            Order: Updated order

        Raises:
            NotFoundError: If order not found
            ValidationError: If status transition is not allowed
        """
        # Convert status string to enum if provided
        if isinstance(new_status, str):
            new_status = OrderStatus.from_string(new_status)

        # Get existing order
        order = await self.order_repository.get_by_id(order_id)
        if not order:
            raise NotFoundError(f"Order not found: {order_id}")

        # Validate transition
        if not order.status.can_transition_to(new_status):
            raise ValidationError(
                f"Cannot transition order from {order.status.value} to {new_status.value}"
            )

        # Update status
        updated_order = await self.order_repository.update_status(order_id, new_status)
        if not updated_order:
            raise NotFoundError(f"Order not found: {order_id}")

        return updated_order


class ConfirmOrder:
    """Use case for confirming an order."""

    def __init__(self, order_repository: OrderRepository):
        """Initialize the use case.

        Args:
            order_repository: Repository for order data
        """
        self.order_repository = order_repository
        self.update_status = UpdateOrderStatus(order_repository)

    async def execute(self, order_id: UUID) -> Order:
        """Confirm an order.

        Args:
            order_id: Order UUID

        Returns:
            Order: Updated order
        """
        return await self.update_status.execute(order_id, OrderStatus.CONFIRMED)


class StartPreparingOrder:
    """Use case for marking order as preparing."""

    def __init__(self, order_repository: OrderRepository):
        """Initialize the use case.

        Args:
            order_repository: Repository for order data
        """
        self.order_repository = order_repository
        self.update_status = UpdateOrderStatus(order_repository)

    async def execute(self, order_id: UUID) -> Order:
        """Mark order as preparing.

        Args:
            order_id: Order UUID

        Returns:
            Order: Updated order
        """
        return await self.update_status.execute(order_id, OrderStatus.PREPARING)


class MarkOrderReady:
    """Use case for marking order as ready."""

    def __init__(self, order_repository: OrderRepository):
        """Initialize the use case.

        Args:
            order_repository: Repository for order data
        """
        self.order_repository = order_repository
        self.update_status = UpdateOrderStatus(order_repository)

    async def execute(self, order_id: UUID) -> Order:
        """Mark order as ready.

        Args:
            order_id: Order UUID

        Returns:
            Order: Updated order
        """
        return await self.update_status.execute(order_id, OrderStatus.READY)


class CompleteOrder:
    """Use case for completing an order."""

    def __init__(self, order_repository: OrderRepository):
        """Initialize the use case.

        Args:
            order_repository: Repository for order data
        """
        self.order_repository = order_repository
        self.update_status = UpdateOrderStatus(order_repository)

    async def execute(self, order_id: UUID) -> Order:
        """Complete an order.

        Args:
            order_id: Order UUID

        Returns:
            Order: Updated order
        """
        return await self.update_status.execute(order_id, OrderStatus.COMPLETED)


class CancelOrder:
    """Use case for cancelling an order."""

    def __init__(self, order_repository: OrderRepository):
        """Initialize the use case.

        Args:
            order_repository: Repository for order data
        """
        self.order_repository = order_repository

    async def execute(self, order_id: UUID) -> Order:
        """Cancel an order.

        Args:
            order_id: Order UUID

        Returns:
            Order: Updated order

        Raises:
            NotFoundError: If order not found
            ValidationError: If order cannot be cancelled
        """
        # Get existing order
        order = await self.order_repository.get_by_id(order_id)
        if not order:
            raise NotFoundError(f"Order not found: {order_id}")

        # Check if can be cancelled
        if order.status.is_final:
            raise ValidationError(
                f"Cannot cancel {order.status.value} order"
            )

        # Update to cancelled
        updated_order = await self.order_repository.update_status(
            order_id, OrderStatus.CANCELLED
        )
        if not updated_order:
            raise NotFoundError(f"Order not found: {order_id}")

        return updated_order
