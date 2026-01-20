"""AIService protocol - Application layer interface for AI features.

Defines the contract for AI services (recommendations, demand prediction).
Concrete implementations are provided in the infrastructure layer.
This is a stub interface for future AI/ML model integration.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import date
from typing import Protocol
from uuid import UUID


@dataclass
class RecommendationItem:
    """A single item recommendation from the AI service."""

    item_id: str
    item_name: str
    score: float  # Confidence score (0.0 to 1.0)
    reason: str  # Human-readable explanation for the recommendation
    category_name: str | None = None
    price: float | None = None
    image_url: str | None = None


@dataclass
class RecommendationResult:
    """Result of AI recommendation request."""

    brand_id: str
    recommendations: list[RecommendationItem]
    model_version: str = "stub-v1.0"
    generated_at: str = ""  # ISO timestamp


@dataclass
class DemandPrediction:
    """Demand prediction for a menu item."""

    item_id: str
    item_name: str
    predicted_quantity: int
    confidence: float  # Confidence score (0.0 to 1.0)
    prediction_date: date


@dataclass
class DemandForecastResult:
    """Result of demand forecasting request."""

    brand_id: str
    predictions: list[DemandPrediction]
    forecast_period_days: int
    model_version: str = "stub-v1.0"
    generated_at: str = ""


@dataclass
class UserPreference:
    """User preference analysis result."""

    user_id: str | None
    preferred_categories: list[str]
    preferred_price_range: tuple[float, float] | None
    dietary_preferences: list[str]
    order_frequency: str  # "frequent", "regular", "occasional", "new"


class AIServiceProtocol(Protocol):
    """Protocol for AI service operations.

    This protocol defines the contract that any AI service implementation
    must follow. The current implementation is a stub that returns mock data.
    Future implementations can integrate with real ML models.
    """

    async def recommend_items(
        self,
        brand_id: UUID,
        user_id: UUID | None = None,
        limit: int = 5,
        context: dict | None = None,
    ) -> RecommendationResult:
        """Get personalized menu item recommendations.

        Args:
            brand_id: Brand UUID to get recommendations for
            user_id: Optional user UUID for personalized recommendations
            limit: Maximum number of recommendations (default: 5)
            context: Optional context dict (e.g., time of day, weather)

        Returns:
            RecommendationResult: List of recommended items with scores
        """
        ...

    async def predict_demand(
        self,
        brand_id: UUID,
        forecast_days: int = 7,
        item_ids: list[str] | None = None,
    ) -> DemandForecastResult:
        """Predict demand for menu items.

        Args:
            brand_id: Brand UUID to predict demand for
            forecast_days: Number of days to forecast (default: 7)
            item_ids: Optional list of specific item IDs to forecast

        Returns:
            DemandForecastResult: Predicted demand for items
        """
        ...

    async def analyze_user_preferences(
        self,
        brand_id: UUID,
        user_id: UUID | None = None,
        order_history: list[dict] | None = None,
    ) -> UserPreference:
        """Analyze user preferences based on order history.

        Args:
            brand_id: Brand UUID
            user_id: Optional user UUID to analyze
            order_history: Optional list of past orders to analyze

        Returns:
            UserPreference: Analyzed user preferences
        """
        ...


class AIService(ABC):
    """Abstract base class for AI service implementations.

    Provides a base class for dependency injection and testing.
    Use this for type hints when injecting AI service dependencies.
    """

    @abstractmethod
    async def recommend_items(
        self,
        brand_id: UUID,
        user_id: UUID | None = None,
        limit: int = 5,
        context: dict | None = None,
    ) -> RecommendationResult:
        """Get personalized menu item recommendations."""
        pass

    @abstractmethod
    async def predict_demand(
        self,
        brand_id: UUID,
        forecast_days: int = 7,
        item_ids: list[str] | None = None,
    ) -> DemandForecastResult:
        """Predict demand for menu items."""
        pass

    @abstractmethod
    async def analyze_user_preferences(
        self,
        brand_id: UUID,
        user_id: UUID | None = None,
        order_history: list[dict] | None = None,
    ) -> UserPreference:
        """Analyze user preferences based on order history."""
        pass
