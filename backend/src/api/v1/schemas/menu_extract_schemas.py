"""Menu extraction schemas for AI-powered menu recognition.

These schemas define the structure for AI menu extraction responses,
including validation, statistics, and draft management.
"""
from datetime import datetime
from typing import Literal, Optional
from uuid import uuid4

from pydantic import BaseModel, Field, field_validator


class ExtractedMenuItem(BaseModel):
    """Single extracted menu item from AI recognition."""

    name: str = Field(..., min_length=1, max_length=100)
    price: float = Field(..., ge=0)
    description: Optional[str] = Field(None, max_length=500)

    @field_validator("price")
    @classmethod
    def validate_price(cls, v: float) -> float:
        """Round price to integer."""
        if v < 0:
            raise ValueError("價格不能為負數")
        return round(v, 0)


class ExtractedCategory(BaseModel):
    """Extracted menu category containing items."""

    name: str = Field(..., min_length=1, max_length=50)
    items: list[ExtractedMenuItem] = Field(default_factory=list)


class ExtractionStats(BaseModel):
    """Statistics for menu extraction results."""

    total_items: int = 0
    items_need_review: int = 0  # Items with price=0 or other issues


class MenuExtractResponse(BaseModel):
    """AI menu extraction response with validation results."""

    success: bool
    categories: list[ExtractedCategory] = Field(default_factory=list)
    raw_text: Optional[str] = None
    error_message: Optional[str] = None
    warnings: list[str] = Field(default_factory=list)
    stats: ExtractionStats = Field(default_factory=ExtractionStats)


# MenuDraft schemas for Phase I & II shared structure


class MenuDraftItem(BaseModel):
    """Draft menu item pending human review."""

    temp_id: str = Field(default_factory=lambda: str(uuid4()))
    name: str = Field(..., min_length=1, max_length=100)
    price: float = Field(..., ge=0)
    description: Optional[str] = Field(None, max_length=500)
    needs_review: bool = False
    review_reason: Optional[str] = None

    @field_validator("price")
    @classmethod
    def validate_price(cls, v: float) -> float:
        """Round price to integer."""
        return round(v, 0)


class MenuDraftCategory(BaseModel):
    """Draft category containing draft items."""

    temp_id: str = Field(default_factory=lambda: str(uuid4()))
    name: str = Field(..., min_length=1, max_length=50)
    items: list[MenuDraftItem] = Field(default_factory=list)


class MenuDraft(BaseModel):
    """Menu draft for Phase I (AI) and Phase II (JSON/Excel) shared structure.

    AI only generates MenuDraft. All data entering the official menu
    must be confirmed by human review.
    """

    source: Literal["ai_extract", "json_import", "excel_import", "manual"]
    brand_id: str
    categories: list[MenuDraftCategory] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    stats: ExtractionStats = Field(default_factory=ExtractionStats)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Phase I specific (AI extraction)
    original_image_url: Optional[str] = None
    raw_text: Optional[str] = None

    # Phase II specific (JSON/Excel import)
    original_file_name: Optional[str] = None


class MenuDraftCreateRequest(BaseModel):
    """Request to create a menu draft from extraction results."""

    brand_id: str
    categories: list[MenuDraftCategory]
    source: Literal["ai_extract", "json_import", "excel_import", "manual"] = "ai_extract"
    original_image_url: Optional[str] = None
    raw_text: Optional[str] = None


class MenuDraftConfirmRequest(BaseModel):
    """Request to confirm a menu draft and save to official menu."""

    draft_id: str
    categories: list[MenuDraftCategory]  # Edited categories from review UI
