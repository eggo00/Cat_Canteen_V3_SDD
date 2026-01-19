"""OrderRepository Implementation - Infrastructure Layer.

SQLAlchemy-based implementation of the OrderRepository interface.
"""

from datetime import date, datetime, timedelta
from decimal import Decimal
from uuid import UUID

from sqlalchemy import and_, cast, Date, extract, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.domain.entities.order import Order
from src.domain.entities.order_item import OrderItem
from src.domain.repositories.order_repository import OrderRepository
from src.domain.value_objects.order_status import OrderStatus
from src.infrastructure.database.models.order_model import OrderItemModel, OrderModel


class OrderRepositoryImpl(OrderRepository):
    """SQLAlchemy implementation of OrderRepository."""

    def __init__(self, session: AsyncSession):
        """Initialize repository with database session.

        Args:
            session: SQLAlchemy async session
        """
        self.session = session

    def _to_domain(self, model: OrderModel) -> Order:
        """Convert SQLAlchemy model to domain entity.

        Args:
            model: OrderModel instance

        Returns:
            Order: Domain entity
        """
        items = [
            OrderItem(
                id=item.id,
                order_id=item.order_id,
                menu_item_id=item.menu_item_id,
                menu_item_name=item.menu_item_name,
                quantity=item.quantity,
                unit_price=item.unit_price,
                customizations=item.customizations or [],
                notes=None,  # Notes not stored in item model currently
            )
            for item in model.order_items
        ]

        return Order(
            id=model.id,
            brand_id=model.brand_id,
            order_number=model.order_number,
            customer_name=model.customer_name,
            customer_phone=model.customer_phone,
            items=items,
            status=OrderStatus.from_string(model.status),
            notes=model.notes,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def _to_model(self, entity: Order) -> OrderModel:
        """Convert domain entity to SQLAlchemy model.

        Args:
            entity: Order domain entity

        Returns:
            OrderModel: SQLAlchemy model
        """
        model = OrderModel(
            id=entity.id,
            brand_id=entity.brand_id,
            order_number=entity.order_number,
            customer_name=entity.customer_name,
            customer_phone=entity.customer_phone,
            status=entity.status.value,
            total_amount=entity.total,
            notes=entity.notes,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

        model.order_items = [
            OrderItemModel(
                id=item.id,
                order_id=entity.id,
                menu_item_id=item.menu_item_id,
                menu_item_name=item.menu_item_name,
                unit_price=item.unit_price,
                quantity=item.quantity,
                customizations=item.customizations if item.customizations else None,
                subtotal=item.subtotal,
            )
            for item in entity.items
        ]

        return model

    async def create(self, order: Order) -> Order:
        """Create a new order in the repository.

        Args:
            order: Order entity to persist

        Returns:
            Order: Created order with generated ID
        """
        model = self._to_model(order)
        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model, ["order_items"])
        return self._to_domain(model)

    async def get_by_id(self, order_id: UUID) -> Order | None:
        """Retrieve an order by its ID.

        Args:
            order_id: Unique identifier of the order

        Returns:
            Order | None: Found order or None if not found
        """
        query = (
            select(OrderModel)
            .options(selectinload(OrderModel.order_items))
            .where(OrderModel.id == order_id)
        )
        result = await self.session.execute(query)
        model = result.scalar_one_or_none()

        if not model:
            return None

        return self._to_domain(model)

    async def get_by_order_number(self, order_number: str) -> Order | None:
        """Retrieve an order by its order number.

        Args:
            order_number: Human-readable order number

        Returns:
            Order | None: Found order or None if not found
        """
        query = (
            select(OrderModel)
            .options(selectinload(OrderModel.order_items))
            .where(OrderModel.order_number == order_number)
        )
        result = await self.session.execute(query)
        model = result.scalar_one_or_none()

        if not model:
            return None

        return self._to_domain(model)

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
        conditions = [OrderModel.brand_id == brand_id]

        if status:
            conditions.append(OrderModel.status == status.value)

        query = (
            select(OrderModel)
            .options(selectinload(OrderModel.order_items))
            .where(and_(*conditions))
            .order_by(OrderModel.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(query)
        models = result.scalars().all()

        return [self._to_domain(model) for model in models]

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
        conditions = [OrderModel.customer_phone == phone]

        if brand_id:
            conditions.append(OrderModel.brand_id == brand_id)

        query = (
            select(OrderModel)
            .options(selectinload(OrderModel.order_items))
            .where(and_(*conditions))
            .order_by(OrderModel.created_at.desc())
            .limit(limit)
        )
        result = await self.session.execute(query)
        models = result.scalars().all()

        return [self._to_domain(model) for model in models]

    async def update(self, order: Order) -> Order:
        """Update an existing order.

        Args:
            order: Order entity with updated data

        Returns:
            Order: Updated order
        """
        # Get existing model
        query = (
            select(OrderModel)
            .options(selectinload(OrderModel.order_items))
            .where(OrderModel.id == order.id)
        )
        result = await self.session.execute(query)
        model = result.scalar_one_or_none()

        if not model:
            # Create if not exists (upsert behavior)
            return await self.create(order)

        # Update model fields
        model.customer_name = order.customer_name
        model.customer_phone = order.customer_phone
        model.status = order.status.value
        model.total_amount = order.total
        model.notes = order.notes
        model.updated_at = order.updated_at

        # Update order items - clear and recreate
        model.order_items.clear()
        for item in order.items:
            model.order_items.append(
                OrderItemModel(
                    id=item.id,
                    order_id=order.id,
                    menu_item_id=item.menu_item_id,
                    menu_item_name=item.menu_item_name,
                    unit_price=item.unit_price,
                    quantity=item.quantity,
                    customizations=item.customizations if item.customizations else None,
                    subtotal=item.subtotal,
                )
            )

        await self.session.commit()
        await self.session.refresh(model, ["order_items"])

        return self._to_domain(model)

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
        query = (
            select(OrderModel)
            .options(selectinload(OrderModel.order_items))
            .where(OrderModel.id == order_id)
        )
        result = await self.session.execute(query)
        model = result.scalar_one_or_none()

        if not model:
            return None

        model.status = status.value
        await self.session.commit()
        await self.session.refresh(model)

        return self._to_domain(model)

    async def delete(self, order_id: UUID) -> bool:
        """Delete an order.

        Args:
            order_id: Order identifier

        Returns:
            bool: True if deleted, False if not found
        """
        query = select(OrderModel).where(OrderModel.id == order_id)
        result = await self.session.execute(query)
        model = result.scalar_one_or_none()

        if not model:
            return False

        await self.session.delete(model)
        await self.session.commit()
        return True

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
        from sqlalchemy import func

        conditions = [OrderModel.brand_id == brand_id]

        if status:
            conditions.append(OrderModel.status == status.value)

        query = select(func.count()).select_from(OrderModel).where(and_(*conditions))
        result = await self.session.execute(query)
        return result.scalar() or 0

    async def get_active_orders_by_brand(self, brand_id: UUID) -> list[Order]:
        """Get all active (non-final) orders for a brand.

        Args:
            brand_id: Brand identifier

        Returns:
            list[Order]: List of active orders
        """
        final_statuses = [OrderStatus.COMPLETED.value, OrderStatus.CANCELLED.value]

        query = (
            select(OrderModel)
            .options(selectinload(OrderModel.order_items))
            .where(
                and_(
                    OrderModel.brand_id == brand_id,
                    OrderModel.status.not_in(final_statuses),
                )
            )
            .order_by(OrderModel.created_at.desc())
        )
        result = await self.session.execute(query)
        models = result.scalars().all()

        return [self._to_domain(model) for model in models]

    # ==================== Analytics Methods ====================

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
        # Convert date range to datetime for comparison
        start_datetime = datetime.combine(start_date, datetime.min.time())
        end_datetime = datetime.combine(end_date, datetime.max.time())

        status_values = [s.value for s in statuses]

        query = (
            select(
                cast(OrderModel.created_at, Date).label("order_date"),
                func.sum(OrderModel.total_amount).label("revenue"),
                func.count(OrderModel.id).label("order_count"),
            )
            .where(
                and_(
                    OrderModel.brand_id == brand_id,
                    OrderModel.created_at >= start_datetime,
                    OrderModel.created_at <= end_datetime,
                    OrderModel.status.in_(status_values),
                )
            )
            .group_by(cast(OrderModel.created_at, Date))
            .order_by(cast(OrderModel.created_at, Date))
        )

        result = await self.session.execute(query)
        rows = result.all()

        return [
            {
                "date": row.order_date,
                "revenue": float(row.revenue or 0),
                "order_count": row.order_count,
            }
            for row in rows
        ]

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
        # Convert date range to datetime for comparison
        start_datetime = datetime.combine(start_date, datetime.min.time())
        end_datetime = datetime.combine(end_date, datetime.max.time())

        status_values = [s.value for s in statuses]

        query = (
            select(
                OrderItemModel.menu_item_id,
                OrderItemModel.menu_item_name,
                func.sum(OrderItemModel.quantity).label("quantity_sold"),
                func.sum(OrderItemModel.subtotal).label("total_revenue"),
            )
            .join(OrderModel, OrderItemModel.order_id == OrderModel.id)
            .where(
                and_(
                    OrderModel.brand_id == brand_id,
                    OrderModel.created_at >= start_datetime,
                    OrderModel.created_at <= end_datetime,
                    OrderModel.status.in_(status_values),
                )
            )
            .group_by(OrderItemModel.menu_item_id, OrderItemModel.menu_item_name)
            .order_by(func.sum(OrderItemModel.quantity).desc())
            .limit(limit)
        )

        result = await self.session.execute(query)
        rows = result.all()

        return [
            {
                "menu_item_id": row.menu_item_id,
                "menu_item_name": row.menu_item_name,
                "quantity_sold": row.quantity_sold,
                "total_revenue": float(row.total_revenue or 0),
            }
            for row in rows
        ]

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
        # Convert date range to datetime for comparison
        start_datetime = datetime.combine(start_date, datetime.min.time())
        end_datetime = datetime.combine(end_date, datetime.max.time())

        status_values = [s.value for s in statuses]

        query = (
            select(
                extract("hour", OrderModel.created_at).label("hour"),
                func.count(OrderModel.id).label("order_count"),
                func.sum(OrderModel.total_amount).label("total_revenue"),
            )
            .where(
                and_(
                    OrderModel.brand_id == brand_id,
                    OrderModel.created_at >= start_datetime,
                    OrderModel.created_at <= end_datetime,
                    OrderModel.status.in_(status_values),
                )
            )
            .group_by(extract("hour", OrderModel.created_at))
            .order_by(extract("hour", OrderModel.created_at))
        )

        result = await self.session.execute(query)
        rows = result.all()

        return [
            {
                "hour": int(row.hour),
                "order_count": row.order_count,
                "total_revenue": float(row.total_revenue or 0),
            }
            for row in rows
        ]
