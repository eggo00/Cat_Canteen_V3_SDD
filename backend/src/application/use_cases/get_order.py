"""GetOrder Use Case - Application Layer.

Handles retrieving order information.
"""

from uuid import UUID

from src.domain.entities.order import Order
from src.domain.exceptions import NotFoundError
from src.domain.repositories.order_repository import OrderRepository
from src.domain.value_objects.order_status import OrderStatus


class GetOrder:
    """Use case for retrieving an order by ID or order number."""

    def __init__(self, order_repository: OrderRepository):
        """Initialize the use case.

        Args:
            order_repository: Repository for order data
        """
        self.order_repository = order_repository

    async def execute_by_id(self, order_id: UUID) -> Order:
        """Get order by ID.

        Args:
            order_id: Order UUID

        Returns:
            Order: Found order

        Raises:
            NotFoundError: If order not found
        """
        order = await self.order_repository.get_by_id(order_id)
        if not order:
            raise NotFoundError(f"Order not found: {order_id}")
        return order

    async def execute_by_order_number(self, order_number: str) -> Order:
        """Get order by order number.

        Args:
            order_number: Human-readable order number

        Returns:
            Order: Found order

        Raises:
            NotFoundError: If order not found
        """
        order = await self.order_repository.get_by_order_number(order_number)
        if not order:
            raise NotFoundError(f"Order not found: {order_number}")
        return order


class GetOrdersByBrand:
    """Use case for retrieving orders for a brand."""

    def __init__(self, order_repository: OrderRepository):
        """Initialize the use case.

        Args:
            order_repository: Repository for order data
        """
        self.order_repository = order_repository

    async def execute(
        self,
        brand_id: UUID,
        status: OrderStatus | str | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Order]:
        """Get orders for a brand.

        Args:
            brand_id: Brand UUID
            status: Optional status filter
            skip: Pagination offset
            limit: Maximum results

        Returns:
            list[Order]: List of orders
        """
        # Convert status string to enum if provided
        if isinstance(status, str):
            status = OrderStatus.from_string(status)

        return await self.order_repository.get_by_brand(
            brand_id=brand_id,
            status=status,
            skip=skip,
            limit=limit,
        )


class GetActiveOrders:
    """Use case for retrieving active orders for a brand."""

    def __init__(self, order_repository: OrderRepository):
        """Initialize the use case.

        Args:
            order_repository: Repository for order data
        """
        self.order_repository = order_repository

    async def execute(self, brand_id: UUID) -> list[Order]:
        """Get active orders for a brand.

        Args:
            brand_id: Brand UUID

        Returns:
            list[Order]: List of active orders
        """
        return await self.order_repository.get_active_orders_by_brand(brand_id)


class GetOrdersByPhone:
    """Use case for retrieving orders by customer phone."""

    def __init__(self, order_repository: OrderRepository):
        """Initialize the use case.

        Args:
            order_repository: Repository for order data
        """
        self.order_repository = order_repository

    async def execute(
        self,
        phone: str,
        brand_id: UUID | None = None,
        limit: int = 10,
    ) -> list[Order]:
        """Get orders for a customer phone number.

        Args:
            phone: Customer phone number
            brand_id: Optional brand filter
            limit: Maximum results

        Returns:
            list[Order]: List of orders
        """
        return await self.order_repository.get_by_customer_phone(
            phone=phone,
            brand_id=brand_id,
            limit=limit,
        )
