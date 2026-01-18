"""Brand API schemas."""
from uuid import UUID

from pydantic import Field, field_validator

from . import BaseSchema, IDSchema, TimestampSchema


class ThemeConfigSchema(BaseSchema):
    """Theme configuration schema."""

    primary_color: str = Field(
        ...,
        description="Primary brand color (hex format)",
        examples=["#FF6B6B"],
        pattern=r"^#[0-9A-Fa-f]{6}$",
    )
    secondary_color: str | None = Field(
        None,
        description="Secondary brand color (hex format)",
        examples=["#4ECDC4"],
        pattern=r"^#[0-9A-Fa-f]{6}$",
    )
    accent_color: str | None = Field(
        None,
        description="Accent color (hex format)",
        examples=["#FFE66D"],
        pattern=r"^#[0-9A-Fa-f]{6}$",
    )
    background_color: str | None = Field(
        None,
        description="Background color (hex format)",
        examples=["#FFFFFF"],
        pattern=r"^#[0-9A-Fa-f]{6}$",
    )
    text_color: str | None = Field(
        None,
        description="Text color (hex format)",
        examples=["#2C3E50"],
        pattern=r"^#[0-9A-Fa-f]{6}$",
    )
    font_family: str | None = Field(
        None,
        description="Font family name",
        examples=["Noto Sans TC, sans-serif"],
        max_length=100,
    )

    @field_validator("primary_color", "secondary_color", "accent_color", "background_color", "text_color")
    @classmethod
    def validate_hex_color(cls, v: str | None) -> str | None:
        """Validate hex color format."""
        if v is not None:
            v = v.upper()
        return v


class BrandCreateRequest(BaseSchema):
    """Request schema for creating a brand."""

    name: str = Field(
        ...,
        description="Brand name",
        examples=["咖啡廳"],
        min_length=1,
        max_length=255,
    )
    slug: str | None = Field(
        None,
        description="URL-friendly slug (auto-generated from name if not provided)",
        examples=["coffee-shop"],
        pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$",
        max_length=255,
    )
    description: str | None = Field(
        None,
        description="Brand description",
        examples=["精品咖啡與甜點專賣店"],
        max_length=1000,
    )
    logo_url: str | None = Field(
        None,
        description="Brand logo URL",
        examples=["https://example.com/logo.png"],
        max_length=2048,
    )
    theme_config: ThemeConfigSchema = Field(
        ...,
        description="Brand theme configuration",
    )


class BrandUpdateRequest(BaseSchema):
    """Request schema for updating a brand."""

    name: str | None = Field(
        None,
        description="Brand name",
        min_length=1,
        max_length=255,
    )
    slug: str | None = Field(
        None,
        description="URL-friendly slug",
        pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$",
        max_length=255,
    )
    description: str | None = Field(
        None,
        description="Brand description",
        max_length=1000,
    )
    logo_url: str | None = Field(
        None,
        description="Brand logo URL",
        max_length=2048,
    )
    theme_config: ThemeConfigSchema | None = Field(
        None,
        description="Brand theme configuration",
    )
    is_active: bool | None = Field(
        None,
        description="Brand active status",
    )


class BrandResponse(IDSchema):
    """Response schema for brand."""

    name: str = Field(..., description="Brand name")
    slug: str = Field(..., description="URL-friendly slug")
    description: str | None = Field(None, description="Brand description")
    logo_url: str | None = Field(None, description="Brand logo URL")
    theme_config: dict = Field(..., description="Brand theme configuration")  # Accept dict with any keys
    is_active: bool = Field(..., description="Brand active status")


class BrandListResponse(BaseSchema):
    """Response schema for list of brands."""

    brands: list[BrandResponse] = Field(..., description="List of brands")
    total: int = Field(..., description="Total number of brands")


__all__ = [
    "ThemeConfigSchema",
    "BrandCreateRequest",
    "BrandUpdateRequest",
    "BrandResponse",
    "BrandListResponse",
]
