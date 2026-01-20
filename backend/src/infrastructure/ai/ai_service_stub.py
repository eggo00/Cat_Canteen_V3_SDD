"""AI Service Stub Implementation.

Provides mock AI responses for development and testing.
This stub will be replaced with real ML model integration in the future.

Performance requirement: Response time ≤ 500ms (SC-009)
"""
from datetime import date, datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.services.ai_service import (
    AIService,
    DemandForecastResult,
    DemandPrediction,
    RecommendationItem,
    RecommendationResult,
    UserPreference,
)
from src.infrastructure.database.models import CategoryModel, MenuItemModel


class AIServiceStub(AIService):
    """Stub implementation of AI service returning mock data.

    This stub provides realistic-looking mock data for:
    - Menu item recommendations
    - Demand predictions
    - User preference analysis

    All responses are designed to match the expected format of a real AI service,
    making it easy to swap this stub with actual ML models in the future.
    """

    # Mock recommendation reasons
    RECOMMENDATION_REASONS = [
        "熱門推薦 - 本週最受歡迎",
        "搭配推薦 - 與您的訂單相配",
        "新品上市 - 限時優惠中",
        "季節限定 - 當季食材製作",
        "店長推薦 - 招牌必點",
        "人氣商品 - 回購率超高",
        "健康首選 - 低卡路里",
        "經典款式 - 不敗的選擇",
    ]

    def __init__(self, session: AsyncSession | None = None):
        """Initialize AI service stub.

        Args:
            session: Optional database session for fetching real menu items
        """
        self.session = session

    async def recommend_items(
        self,
        brand_id: UUID,
        user_id: UUID | None = None,
        limit: int = 5,
        context: dict | None = None,
    ) -> RecommendationResult:
        """Get mock personalized menu item recommendations.

        If a database session is provided, returns recommendations based on
        actual menu items. Otherwise, returns generic mock data.

        Args:
            brand_id: Brand UUID to get recommendations for
            user_id: Optional user UUID (unused in stub)
            limit: Maximum number of recommendations
            context: Optional context dict (unused in stub)

        Returns:
            RecommendationResult: Mock recommendations
        """
        recommendations = []

        if self.session:
            # Fetch real menu items from database
            stmt = (
                select(MenuItemModel)
                .join(CategoryModel)
                .where(CategoryModel.brand_id == brand_id)
                .where(MenuItemModel.is_available == True)
                .limit(limit)
            )
            result = await self.session.execute(stmt)
            items = result.scalars().all()

            for i, item in enumerate(items):
                score = 0.95 - (i * 0.05)  # Decreasing confidence scores
                reason_idx = i % len(self.RECOMMENDATION_REASONS)

                recommendations.append(
                    RecommendationItem(
                        item_id=str(item.id),
                        item_name=item.name,
                        score=round(score, 2),
                        reason=self.RECOMMENDATION_REASONS[reason_idx],
                        category_name=item.category.name if item.category else None,
                        price=float(item.price) if item.price else None,
                        image_url=item.image_url,
                    )
                )
        else:
            # Return generic mock recommendations
            mock_items = [
                ("招牌拿鐵", "飲料", 120.0),
                ("經典美式", "飲料", 100.0),
                ("抹茶歐蕾", "飲料", 130.0),
                ("焦糖瑪奇朵", "飲料", 140.0),
                ("提拉米蘇", "甜點", 150.0),
            ]

            for i, (name, category, price) in enumerate(mock_items[:limit]):
                score = 0.95 - (i * 0.05)
                reason_idx = i % len(self.RECOMMENDATION_REASONS)

                recommendations.append(
                    RecommendationItem(
                        item_id=f"mock-item-{i+1}",
                        item_name=name,
                        score=round(score, 2),
                        reason=self.RECOMMENDATION_REASONS[reason_idx],
                        category_name=category,
                        price=price,
                        image_url=None,
                    )
                )

        return RecommendationResult(
            brand_id=str(brand_id),
            recommendations=recommendations,
            model_version="stub-v1.0",
            generated_at=datetime.utcnow().isoformat() + "Z",
        )

    async def predict_demand(
        self,
        brand_id: UUID,
        forecast_days: int = 7,
        item_ids: list[str] | None = None,
    ) -> DemandForecastResult:
        """Get mock demand predictions.

        Args:
            brand_id: Brand UUID to predict demand for
            forecast_days: Number of days to forecast
            item_ids: Optional list of specific item IDs

        Returns:
            DemandForecastResult: Mock demand predictions
        """
        predictions = []
        base_date = date.today()

        # Generate mock predictions
        mock_items = [
            ("mock-item-1", "招牌拿鐵", 50),
            ("mock-item-2", "經典美式", 40),
            ("mock-item-3", "抹茶歐蕾", 30),
            ("mock-item-4", "焦糖瑪奇朵", 25),
            ("mock-item-5", "提拉米蘇", 20),
        ]

        items_to_predict = mock_items
        if item_ids:
            items_to_predict = [
                (id, f"Item {id}", 30) for id in item_ids
            ]

        for item_id, item_name, base_qty in items_to_predict:
            # Simulate varying predictions with confidence
            import random
            random.seed(hash(item_id) % 1000)  # Deterministic for testing

            predictions.append(
                DemandPrediction(
                    item_id=item_id,
                    item_name=item_name,
                    predicted_quantity=base_qty + random.randint(-5, 10),
                    confidence=round(0.75 + random.random() * 0.2, 2),
                    prediction_date=base_date,
                )
            )

        return DemandForecastResult(
            brand_id=str(brand_id),
            predictions=predictions,
            forecast_period_days=forecast_days,
            model_version="stub-v1.0",
            generated_at=datetime.utcnow().isoformat() + "Z",
        )

    async def analyze_user_preferences(
        self,
        brand_id: UUID,
        user_id: UUID | None = None,
        order_history: list[dict] | None = None,
    ) -> UserPreference:
        """Get mock user preference analysis.

        Args:
            brand_id: Brand UUID
            user_id: Optional user UUID
            order_history: Optional list of past orders

        Returns:
            UserPreference: Mock user preferences
        """
        # Return mock preferences
        return UserPreference(
            user_id=str(user_id) if user_id else None,
            preferred_categories=["飲料", "甜點"],
            preferred_price_range=(80.0, 150.0),
            dietary_preferences=["無糖選項", "低卡"],
            order_frequency="regular" if user_id else "new",
        )


# Singleton instance for dependency injection
_ai_service_stub: AIServiceStub | None = None


def get_ai_service(session: AsyncSession | None = None) -> AIServiceStub:
    """Get AI service instance.

    Factory function for dependency injection.
    In production, this can be swapped with a real ML service.

    Args:
        session: Optional database session

    Returns:
        AIServiceStub: AI service instance
    """
    return AIServiceStub(session=session)
