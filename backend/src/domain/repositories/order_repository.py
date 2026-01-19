"""OrderRepository Interface - Domain Layer.

Defines the abstract interface for order persistence operations.
"""

from abc import ABC, abstractmethod
from datetime import date
from uuid import UUID

from src.domain.entities.order import Order
from src.domain.value_objects.order_status import OrderStatus


class OrderRepository(ABC):
    """Abstract repository interface for Order entity.

    Implementations should handle persistence to any data store
    (database, file, external API, etc.)
    """

    @abstractmethod
    async def create(self, order: Order) -> Order:
        """Create a new order in the repository.

        Args:
            order: Order entity to persist

        Returns:
            Order: Created order with generated ID
        """
        pass

    @abstractmethod
    async def get_by_id(self, order_id: UUID) -> Order | None:
        """Retrieve an order by its ID.

        Args:
            order_id: Unique identifier of the order

        Returns:
            Order | None: Found order or None if not found
        """
        pass

    @abstractmethod
    async def get_by_order_number(self, order_number: str) -> Order | None:
        """Retrieve an order by its order number.

        Args:
            order_number: Human-readable order number

        Returns:
            Order | None: Found order or None if not found
        """
        pass

    @abstractmethod
    async def get_by_brand(
        self,
        brand_id: UUID,
        status: OrderStatus | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Order]:
        """Retrieve orders for a brand.

        Args:
            brand_id: Brand identifier
            status: Optional status filter
            skip: Number of records to skip (for pagination)
            limit: Maximum number of records to return

        Returns:
            list[Order]: List of orders for the brand
        """
        pass

    @abstractmethod
    async def get_by_customer_phone(
        self,
        phone: str,
        brand_id: UUID | None = None,
        limit: int = 10,
    ) -> list[Order]:
        """Retrieve orders by customer phone number.

        Args:
            phone: Customer phone number
            brand_id: Optional brand filter
            limit: Maximum number of records to return

        Returns:
            list[Order]: List of orders for the customer
        """
        pass

    @abstractmethod
    async def update(self, order: Order) -> Order:
        """Update an existing order.

        Args:
            order: Order entity with updated data

        Returns:
            Order: Updated order
        """
        pass

    @abstractmethod
    async def update_status(
        self, order_id: UUID, status: OrderStatus
    ) -> Order | None:
        """Update order status.

        Args:
            order_id: Order identifier
            status: New order status

        Returns:
            Order | None: Updated order or None if not found
        """
        pass

    @abstractmethod
    async def delete(self, order_id: UUID) -> bool:
        """Delete an order.

        Note: Orders should typically not be deleted, but this method
        is provided for administrative purposes.

        Args:
            order_id: Order identifier

        Returns:
            bool: True if deleted, False if not found
        """
        pass

    @abstractmethod
    async def count_by_brand(
        self,
        brand_id: UUID,
        status: OrderStatus | None = None,
    ) -> int:
        """Count orders for a brand.

        Args:
            brand_id: Brand identifier
            status: Optional status filter

        Returns:
            int: Number of orders matching criteria
        """
        pass

    @abstractmethod
    async def get_active_orders_by_brand(self, brand_id: UUID) -> list[Order]:
        """Get all active (non-final) orders for a brand.

        Args:
            brand_id: Brand identifier

        Returns:
            list[Order]: List of active orders
        """
        pass

    # ==================== Analytics Methods ====================

    @abstractmethod
    async def get_revenue_by_date_range(
        self,
        brand_id: UUID,
        start_date: date,
        end_date: date,
        statuses: list[OrderStatus],
    ) -> list[dict]:
        """Get revenue aggregated by date.

        Args:
            brand_id: Brand identifier
            start_date: Start of date range
            end_date: End of date range
            statuses: Order statuses to include

        Returns:
            list[dict]: List of dicts with 'date', 'revenue', 'order_count'
        """
        pass

    @abstractmethod
    async def get_top_items_by_date_range(
        self,
        brand_id: UUID,
        start_date: date,
        end_date: date,
        statuses: list[OrderStatus],
        limit: int = 10,
    ) -> list[dict]:
        """Get top-selling items aggregated by quantity.

        Args:
            brand_id: Brand identifier
            start_date: Start of date range
            end_date: End of date range
            statuses: Order statuses to include
            limit: Maximum number of items to return

        Returns:
            list[dict]: List of dicts with 'menu_item_id', 'menu_item_name',
                       'quantity_sold', 'total_revenue'
        """
        pass

    @abstractmethod
    async def get_orders_by_hour(
        self,
        brand_id: UUID,
        start_date: date,
        end_date: date,
        statuses: list[OrderStatus],
    ) -> list[dict]:
        """Get order distribution by hour of day.

        Args:
            brand_id: Brand identifier
            start_date: Start of date range
            end_date: End of date range
            statuses: Order statuses to include

        Returns:
            list[dict]: List of dicts with 'hour' (0-23), 'order_count', 'total_revenue'
        """
        pass
