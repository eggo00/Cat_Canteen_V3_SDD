"""API v1 Pydantic schemas package.

Base schemas and common models for API requests and responses.
"""
from datetime import datetime
from typing import Generic, TypeVar
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

# Generic type for paginated responses
T = TypeVar("T")


class BaseSchema(BaseModel):
    """Base Pydantic schema with common configuration."""

    model_config = ConfigDict(
        from_attributes=True,  # Allow ORM mode (formerly orm_mode)
        populate_by_name=True,  # Allow field population by alias or name
        use_enum_values=True,  # Use enum values instead of enum objects
    )


class TimestampSchema(BaseSchema):
    """Schema with timestamp fields."""

    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")


class IDSchema(BaseSchema):
    """Schema with UUID ID field."""

    id: UUID = Field(..., description="Unique identifier")


class PaginationParams(BaseModel):
    """Query parameters for pagination."""

    page: int = Field(1, ge=1, description="Page number (starts at 1)")
    page_size: int = Field(20, ge=1, le=100, description="Items per page (max 100)")

    @property
    def offset(self) -> int:
        """Calculate offset for database query."""
        return (self.page - 1) * self.page_size

    @property
    def limit(self) -> int:
        """Get limit for database query."""
        return self.page_size


class PaginatedResponse(BaseSchema, Generic[T]):
    """Generic paginated response wrapper."""

    items: list[T] = Field(..., description="List of items")
    total: int = Field(..., description="Total number of items")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Items per page")
    total_pages: int = Field(..., description="Total number of pages")

    @classmethod
    def create(
        cls,
        items: list[T],
        total: int,
        page: int,
        page_size: int,
    ) -> "PaginatedResponse[T]":
        """Create paginated response.

        Args:
            items: List of items for current page
            total: Total number of items
            page: Current page number
            page_size: Items per page

        Returns:
            PaginatedResponse: Paginated response object
        """
        total_pages = (total + page_size - 1) // page_size  # Ceiling division
        return cls(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )


class MessageResponse(BaseSchema):
    """Simple message response."""

    message: str = Field(..., description="Response message")


class SuccessResponse(BaseSchema):
    """Success response with optional data."""

    success: bool = Field(True, description="Operation success status")
    message: str = Field(..., description="Success message")
    data: dict | None = Field(None, description="Optional response data")


from .brand_schemas import *  # noqa: F401, F403
from .menu_schemas import *  # noqa: F401, F403

__all__ = [
    "BaseSchema",
    "TimestampSchema",
    "IDSchema",
    "PaginationParams",
    "PaginatedResponse",
    "MessageResponse",
    "SuccessResponse",
]
