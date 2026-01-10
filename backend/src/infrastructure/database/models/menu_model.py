"""SQLAlchemy models for Menu entities (Category, MenuItem, CustomizationOption)."""
from decimal import Decimal

from sqlalchemy import Boolean, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin, UUIDMixin


class CategoryModel(Base, UUIDMixin, TimestampMixin):
    """Menu category model (e.g., '飲料', '主餐', '甜點')."""

    __tablename__ = "menu_categories"

    # Foreign Key
    brand_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("brands.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Basic Information
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    display_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    brand: Mapped["BrandModel"] = relationship("BrandModel", back_populates="categories")
    menu_items: Mapped[list["MenuItemModel"]] = relationship(
        "MenuItemModel", back_populates="category", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        """String representation of Category."""
        return f"<Category(id={self.id}, name={self.name}, brand_id={self.brand_id})>"


class MenuItemModel(Base, UUIDMixin, TimestampMixin):
    """Menu item model representing a specific dish or product."""

    __tablename__ = "menu_items"

    # Foreign Key
    category_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("menu_categories.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Basic Information
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    image_url: Mapped[str | None] = mapped_column(String(2048), nullable=True)

    # Display
    display_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Status
    is_available: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    # Relationships
    category: Mapped["CategoryModel"] = relationship("CategoryModel", back_populates="menu_items")
    customization_options: Mapped[list["CustomizationOptionModel"]] = relationship(
        "CustomizationOptionModel", back_populates="menu_item", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        """String representation of MenuItem."""
        return f"<MenuItem(id={self.id}, name={self.name}, price={self.price})>"


class CustomizationOptionModel(Base, UUIDMixin, TimestampMixin):
    """Customization option model (e.g., toppings, sweetness, temperature)."""

    __tablename__ = "customization_options"

    # Foreign Key
    menu_item_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("menu_items.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Type and Name
    option_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="Type of option (e.g., 'topping', 'sweetness', 'temperature')",
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)

    # Pricing
    price_adjustment: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), default=0, nullable=False, comment="Additional cost for this option"
    )

    # Constraints (stored as JSONB for flexibility)
    constraints: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True,
        comment="Constraints like mutually exclusive options",
    )

    # Display
    display_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Relationships
    menu_item: Mapped["MenuItemModel"] = relationship(
        "MenuItemModel", back_populates="customization_options"
    )

    def __repr__(self) -> str:
        """String representation of CustomizationOption."""
        return f"<CustomizationOption(id={self.id}, type={self.option_type}, name={self.name})>"
