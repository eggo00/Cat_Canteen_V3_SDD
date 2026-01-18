"""Menu API schemas."""
from decimal import Decimal
from uuid import UUID

from pydantic import Field, field_validator

from . import BaseSchema, IDSchema


class CustomizationOptionSchema(BaseSchema):
    """Customization option schema."""

    option_type: str = Field(
        ...,
        description="Type of option (e.g., 'size', 'sweetness', 'ice')",
        examples=["sweetness"],
        max_length=50,
    )
    name: str = Field(
        ...,
        description="Display name of the option",
        examples=["半糖"],
        min_length=1,
        max_length=100,
    )
    price_adjustment: float = Field(
        ...,
        description="Price adjustment for this option",
        examples=[0.0, 10.0, -5.0],
    )


class CustomizationOptionResponse(IDSchema):
    """Customization option response schema."""

    option_type: str = Field(..., description="Type of option")
    name: str = Field(..., description="Display name of the option")
    price_adjustment: float = Field(..., description="Price adjustment")


class MenuItemSchema(BaseSchema):
    """Menu item schema for create/update."""

    name: str = Field(
        ...,
        description="Item name",
        examples=["美式咖啡"],
        min_length=1,
        max_length=255,
    )
    description: str | None = Field(
        None,
        description="Item description",
        examples=["香醇美式咖啡"],
        max_length=1000,
    )
    price: float = Field(
        ...,
        description="Item price",
        examples=[100.0],
        ge=0,
    )
    display_order: int = Field(
        ...,
        description="Display order in category",
        examples=[1],
        ge=0,
    )
    customization_options: list[CustomizationOptionSchema] = Field(
        default_factory=list,
        description="List of customization options",
    )

    @field_validator("price")
    @classmethod
    def validate_price(cls, v: float) -> float:
        """Validate price has at most 2 decimal places."""
        if round(v, 2) != v:
            raise ValueError("Price must have at most 2 decimal places")
        return v


class MenuItemResponse(IDSchema):
    """Menu item response schema."""

    name: str = Field(..., description="Item name")
    description: str | None = Field(None, description="Item description")
    price: float = Field(..., description="Item price")
    display_order: int = Field(..., description="Display order")
    customization_options: list[CustomizationOptionResponse] = Field(
        default_factory=list,
        description="List of customization options",
    )


class CategorySchema(BaseSchema):
    """Category schema for create/update."""

    name: str = Field(
        ...,
        description="Category name",
        examples=["飲料"],
        min_length=1,
        max_length=255,
    )
    description: str | None = Field(
        None,
        description="Category description",
        examples=["各式飲品"],
        max_length=1000,
    )
    display_order: int = Field(
        ...,
        description="Display order in menu",
        examples=[1],
        ge=0,
    )
    menu_items: list[MenuItemSchema] = Field(
        default_factory=list,
        description="List of menu items",
    )


class CategoryResponse(IDSchema):
    """Category response schema."""

    name: str = Field(..., description="Category name")
    description: str | None = Field(None, description="Category description")
    display_order: int = Field(..., description="Display order")
    menu_items: list[MenuItemResponse] = Field(
        default_factory=list,
        description="List of menu items",
    )


class MenuUploadRequest(BaseSchema):
    """Request schema for uploading complete menu."""

    categories: list[CategorySchema] = Field(
        ...,
        description="List of categories with menu items",
        min_length=1,
    )


class MenuResponse(BaseSchema):
    """Response schema for complete menu."""

    categories: list[CategoryResponse] = Field(
        default_factory=list,
        description="List of categories with menu items",
    )


class CategoryCreateRequest(BaseSchema):
    """Request schema for creating a category."""

    name: str = Field(
        ...,
        description="Category name",
        min_length=1,
        max_length=255,
    )
    description: str | None = Field(
        None,
        description="Category description",
        max_length=1000,
    )
    display_order: int = Field(
        ...,
        description="Display order in menu",
        ge=0,
    )


class CategoryUpdateRequest(BaseSchema):
    """Request schema for updating a category."""

    name: str | None = Field(
        None,
        description="Category name",
        min_length=1,
        max_length=255,
    )
    description: str | None = Field(
        None,
        description="Category description",
        max_length=1000,
    )
    display_order: int | None = Field(
        None,
        description="Display order in menu",
        ge=0,
    )


__all__ = [
    "CustomizationOptionSchema",
    "CustomizationOptionResponse",
    "MenuItemSchema",
    "MenuItemResponse",
    "CategorySchema",
    "CategoryResponse",
    "MenuUploadRequest",
    "MenuResponse",
    "CategoryCreateRequest",
    "CategoryUpdateRequest",
]
