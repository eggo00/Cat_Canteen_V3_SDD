"""SQLAlchemy models for Order entities."""
from decimal import Decimal

from sqlalchemy import ForeignKey, Integer, JSON, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin, UUIDMixin


class OrderModel(Base, UUIDMixin, TimestampMixin):
    """Order model representing a customer order."""

    __tablename__ = "orders"

    # Foreign Key
    brand_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("brands.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Order Identification
    order_number: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False, index=True, comment="Format: CC20260108-0001"
    )

    # Customer Information (no auth required, so stored directly)
    customer_name: Mapped[str] = mapped_column(String(255), nullable=False)
    customer_phone: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    customer_email: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Order Status
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="pending",
        index=True,
        comment="pending, preparing, completed, cancelled",
    )

    # Pricing
    total_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)

    # Additional Notes
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    brand: Mapped["BrandModel"] = relationship("BrandModel", back_populates="orders")
    order_items: Mapped[list["OrderItemModel"]] = relationship(
        "OrderItemModel", back_populates="order", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        """String representation of Order."""
        return f"<Order(id={self.id}, order_number={self.order_number}, status={self.status})>"


class OrderItemModel(Base, UUIDMixin, TimestampMixin):
    """Order item model representing a single item in an order."""

    __tablename__ = "order_items"

    # Foreign Keys
    order_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, index=True
    )
    menu_item_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("menu_items.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # Item Information (denormalized for historical accuracy)
    menu_item_name: Mapped[str] = mapped_column(String(255), nullable=False)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    # Customizations (stored as JSONB)
    customizations: Mapped[dict | None] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),  # PostgreSQL 用 JSONB，其他用 JSON
        nullable=True,
        comment="Customer customizations (toppings, sweetness, etc.)",
    )

    # Calculated
    subtotal: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), nullable=False, comment="unit_price * quantity + customizations"
    )

    # Relationships
    order: Mapped["OrderModel"] = relationship("OrderModel", back_populates="order_items")
    menu_item: Mapped["MenuItemModel"] = relationship("MenuItemModel")

    def __repr__(self) -> str:
        """String representation of OrderItem."""
        return f"<OrderItem(id={self.id}, name={self.menu_item_name}, quantity={self.quantity})>"
