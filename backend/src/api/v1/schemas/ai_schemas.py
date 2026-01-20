"""AI API schemas.

Pydantic schemas for AI recommendation and prediction endpoints.
"""
from datetime import date as date_type
from uuid import UUID

from pydantic import Field

from . import BaseSchema


class RecommendationItemResponse(BaseSchema):
    """Response schema for a single recommendation item."""

    item_id: str = Field(..., description="Menu item ID")
    item_name: str = Field(..., description="Menu item name")
    score: float = Field(..., ge=0.0, le=1.0, description="Confidence score (0-1)")
    reason: str = Field(..., description="Recommendation reason")
    category_name: str | None = Field(None, description="Category name")
    price: float | None = Field(None, description="Item price")
    image_url: str | None = Field(None, description="Item image URL")


class RecommendationResponse(BaseSchema):
    """Response schema for AI recommendations."""

    brand_id: str = Field(..., description="Brand ID")
    recommendations: list[RecommendationItemResponse] = Field(
        ..., description="List of recommended items"
    )
    model_version: str = Field(..., description="AI model version")
    generated_at: str = Field(..., description="ISO timestamp of generation")


class RecommendationRequest(BaseSchema):
    """Request schema for getting recommendations."""

    user_id: UUID | None = Field(None, description="Optional user ID for personalization")
    limit: int = Field(5, ge=1, le=20, description="Number of recommendations")
    context: dict | None = Field(None, description="Optional context (time, weather, etc.)")


class DemandPredictionItem(BaseSchema):
    """Response schema for a single demand prediction."""

    item_id: str = Field(..., description="Menu item ID")
    item_name: str = Field(..., description="Menu item name")
    predicted_quantity: int = Field(..., ge=0, description="Predicted demand quantity")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Prediction confidence")
    prediction_date: date_type = Field(..., description="Date of prediction")


class DemandForecastResponse(BaseSchema):
    """Response schema for demand forecast."""

    brand_id: str = Field(..., description="Brand ID")
    predictions: list[DemandPredictionItem] = Field(
        ..., description="List of demand predictions"
    )
    forecast_period_days: int = Field(..., description="Forecast period in days")
    model_version: str = Field(..., description="AI model version")
    generated_at: str = Field(..., description="ISO timestamp of generation")


class DemandForecastRequest(BaseSchema):
    """Request schema for demand forecast."""

    forecast_days: int = Field(7, ge=1, le=30, description="Days to forecast")
    item_ids: list[str] | None = Field(None, description="Specific item IDs to forecast")


class UserPreferenceResponse(BaseSchema):
    """Response schema for user preference analysis."""

    user_id: str | None = Field(None, description="User ID if analyzed")
    preferred_categories: list[str] = Field(..., description="Preferred categories")
    preferred_price_range: tuple[float, float] | None = Field(
        None, description="Preferred price range (min, max)"
    )
    dietary_preferences: list[str] = Field(..., description="Dietary preferences")
    order_frequency: str = Field(
        ...,
        description="Order frequency (frequent, regular, occasional, new)"
    )


class AIStatusResponse(BaseSchema):
    """Response schema for AI service status."""

    status: str = Field(..., description="Service status (ok, degraded, unavailable)")
    model_version: str = Field(..., description="Current model version")
    features_available: list[str] = Field(..., description="Available AI features")
    is_stub: bool = Field(..., description="Whether using stub implementation")


__all__ = [
    "RecommendationItemResponse",
    "RecommendationResponse",
    "RecommendationRequest",
    "DemandPredictionItem",
    "DemandForecastResponse",
    "DemandForecastRequest",
    "UserPreferenceResponse",
    "AIStatusResponse",
]
