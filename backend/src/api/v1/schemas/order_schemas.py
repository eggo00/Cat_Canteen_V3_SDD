"""Order API Schemas - Pydantic models for request/response validation."""

from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class OrderStatusEnum(str, Enum):
    """Order status enumeration for API."""

    PENDING = "pending"
    CONFIRMED = "confirmed"
    PREPARING = "preparing"
    READY = "ready"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class CustomizationSchema(BaseModel):
    """Schema for customization selection."""

    option_id: UUID = Field(..., description="Customization option ID")
    name: str = Field(..., description="Customization name")
    price_adjustment: float = Field(default=0, description="Price adjustment")


class CreateOrderItemSchema(BaseModel):
    """Schema for creating an order item."""

    menu_item_id: UUID = Field(..., description="Menu item ID")
    quantity: int = Field(default=1, ge=1, le=100, description="Quantity to order")
    customizations: list[CustomizationSchema] | None = Field(
        default=None, description="Selected customizations"
    )
    notes: str | None = Field(
        default=None, max_length=500, description="Special instructions"
    )


class CreateOrderRequest(BaseModel):
    """Request schema for creating an order."""

    customer_name: str = Field(
        ..., min_length=1, max_length=255, description="Customer name"
    )
    customer_phone: str = Field(
        ..., min_length=10, max_length=20, description="Customer phone (Taiwan mobile)"
    )
    items: list[CreateOrderItemSchema] = Field(
        ..., min_length=1, description="Order items"
    )
    notes: str | None = Field(
        default=None, max_length=1000, description="Order notes"
    )

    @field_validator("customer_phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        """Validate Taiwan mobile phone format."""
        import re

        digits_only = re.sub(r"[\s\-\(\)]+", "", v)
        if not re.match(r"^09\d{8}$", digits_only):
            raise ValueError("Invalid phone format. Use Taiwan mobile format (e.g., 0912345678)")
        return digits_only


class UpdateOrderStatusRequest(BaseModel):
    """Request schema for updating order status."""

    status: OrderStatusEnum = Field(..., description="New order status")


class OrderItemResponse(BaseModel):
    """Response schema for an order item."""

    id: UUID
    menu_item_id: UUID
    menu_item_name: str
    quantity: int
    unit_price: float
    subtotal: float
    customizations: list[dict] = Field(default_factory=list)
    notes: str | None = None


class OrderResponse(BaseModel):
    """Response schema for an order."""

    id: UUID
    brand_id: UUID
    order_number: str
    customer_name: str
    customer_phone: str
    items: list[OrderItemResponse]
    status: OrderStatusEnum
    status_display: str
    notes: str | None = None
    total: float
    item_count: int
    created_at: datetime
    updated_at: datetime


class OrderListResponse(BaseModel):
    """Response schema for a list of orders."""

    orders: list[OrderResponse]
    total: int
    skip: int
    limit: int


class OrderSummaryResponse(BaseModel):
    """Simplified order response for lists."""

    id: UUID
    order_number: str
    customer_name: str
    status: OrderStatusEnum
    status_display: str
    total: float
    item_count: int
    created_at: datetime
