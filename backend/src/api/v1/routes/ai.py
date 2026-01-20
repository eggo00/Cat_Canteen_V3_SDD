"""AI API routes.

Provides endpoints for AI-powered recommendations and predictions.
Currently uses stub implementation; will be replaced with real ML models.

Performance requirement: Response time ≤ 500ms (SC-009)
"""
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.v1.schemas.ai_schemas import (
    AIStatusResponse,
    DemandForecastRequest,
    DemandForecastResponse,
    DemandPredictionItem,
    RecommendationItemResponse,
    RecommendationRequest,
    RecommendationResponse,
    UserPreferenceResponse,
)
from src.domain.exceptions import NotFoundError
from src.infrastructure.ai.ai_service_stub import AIServiceStub, get_ai_service
from src.infrastructure.database.session import get_async_session
from src.infrastructure.repositories.brand_repository_impl import BrandRepositoryImpl

router = APIRouter(prefix="/ai", tags=["AI"])


async def get_ai_service_with_session(
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> AIServiceStub:
    """Dependency to get AI service with database session."""
    return get_ai_service(session=session)


@router.get(
    "/status",
    response_model=AIStatusResponse,
    summary="Get AI service status",
    description="Check the status of AI services and available features",
)
async def get_ai_status() -> AIStatusResponse:
    """Get AI service status.

    Returns:
        AIStatusResponse: Current AI service status
    """
    return AIStatusResponse(
        status="ok",
        model_version="stub-v1.0",
        features_available=[
            "recommendations",
            "demand_forecast",
            "user_preferences",
        ],
        is_stub=True,
    )


@router.get(
    "/brands/{brand_id}/recommendations",
    response_model=RecommendationResponse,
    summary="Get menu recommendations",
    description="Get AI-powered menu item recommendations for a brand",
)
async def get_recommendations(
    brand_id: UUID,
    session: Annotated[AsyncSession, Depends(get_async_session)],
    user_id: UUID | None = Query(None, description="User ID for personalization"),
    limit: int = Query(5, ge=1, le=20, description="Number of recommendations"),
) -> RecommendationResponse:
    """Get personalized menu recommendations.

    Args:
        brand_id: Brand UUID to get recommendations for
        session: Database session
        user_id: Optional user ID for personalized recommendations
        limit: Maximum number of recommendations (1-20)

    Returns:
        RecommendationResponse: AI-generated recommendations

    Raises:
        HTTPException: If brand not found
    """
    # Verify brand exists
    brand_repository = BrandRepositoryImpl(session)
    brand = await brand_repository.get_by_id(brand_id)

    if brand is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Brand not found: {brand_id}",
        )

    # Get AI recommendations
    ai_service = get_ai_service(session=session)
    result = await ai_service.recommend_items(
        brand_id=brand_id,
        user_id=user_id,
        limit=limit,
    )

    # Convert to response schema
    return RecommendationResponse(
        brand_id=result.brand_id,
        recommendations=[
            RecommendationItemResponse(
                item_id=item.item_id,
                item_name=item.item_name,
                score=item.score,
                reason=item.reason,
                category_name=item.category_name,
                price=item.price,
                image_url=item.image_url,
            )
            for item in result.recommendations
        ],
        model_version=result.model_version,
        generated_at=result.generated_at,
    )


@router.get(
    "/brands/slug/{slug}/recommendations",
    response_model=RecommendationResponse,
    summary="Get menu recommendations by slug",
    description="Get AI-powered menu item recommendations for a brand using slug",
)
async def get_recommendations_by_slug(
    slug: str,
    session: Annotated[AsyncSession, Depends(get_async_session)],
    user_id: UUID | None = Query(None, description="User ID for personalization"),
    limit: int = Query(5, ge=1, le=20, description="Number of recommendations"),
) -> RecommendationResponse:
    """Get personalized menu recommendations by brand slug.

    This is the primary endpoint for frontend integration.

    Args:
        slug: Brand slug to get recommendations for
        session: Database session
        user_id: Optional user ID for personalized recommendations
        limit: Maximum number of recommendations (1-20)

    Returns:
        RecommendationResponse: AI-generated recommendations

    Raises:
        HTTPException: If brand not found
    """
    # Find brand by slug
    brand_repository = BrandRepositoryImpl(session)
    brand = await brand_repository.get_by_slug(slug)

    if brand is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Brand not found: {slug}",
        )

    # Get AI recommendations
    ai_service = get_ai_service(session=session)
    result = await ai_service.recommend_items(
        brand_id=brand.id,
        user_id=user_id,
        limit=limit,
    )

    # Convert to response schema
    return RecommendationResponse(
        brand_id=result.brand_id,
        recommendations=[
            RecommendationItemResponse(
                item_id=item.item_id,
                item_name=item.item_name,
                score=item.score,
                reason=item.reason,
                category_name=item.category_name,
                price=item.price,
                image_url=item.image_url,
            )
            for item in result.recommendations
        ],
        model_version=result.model_version,
        generated_at=result.generated_at,
    )


@router.get(
    "/brands/{brand_id}/demand-forecast",
    response_model=DemandForecastResponse,
    summary="Get demand forecast",
    description="Get AI-powered demand predictions for menu items",
)
async def get_demand_forecast(
    brand_id: UUID,
    session: Annotated[AsyncSession, Depends(get_async_session)],
    forecast_days: int = Query(7, ge=1, le=30, description="Days to forecast"),
) -> DemandForecastResponse:
    """Get demand predictions for menu items.

    Args:
        brand_id: Brand UUID to forecast for
        session: Database session
        forecast_days: Number of days to forecast (1-30)

    Returns:
        DemandForecastResponse: AI-generated demand predictions

    Raises:
        HTTPException: If brand not found
    """
    # Verify brand exists
    brand_repository = BrandRepositoryImpl(session)
    brand = await brand_repository.get_by_id(brand_id)

    if brand is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Brand not found: {brand_id}",
        )

    # Get AI predictions
    ai_service = get_ai_service(session=session)
    result = await ai_service.predict_demand(
        brand_id=brand_id,
        forecast_days=forecast_days,
    )

    # Convert to response schema
    return DemandForecastResponse(
        brand_id=result.brand_id,
        predictions=[
            DemandPredictionItem(
                item_id=pred.item_id,
                item_name=pred.item_name,
                predicted_quantity=pred.predicted_quantity,
                confidence=pred.confidence,
                prediction_date=pred.prediction_date,
            )
            for pred in result.predictions
        ],
        forecast_period_days=result.forecast_period_days,
        model_version=result.model_version,
        generated_at=result.generated_at,
    )


@router.get(
    "/brands/{brand_id}/user-preferences",
    response_model=UserPreferenceResponse,
    summary="Get user preferences",
    description="Analyze user preferences based on order history",
)
async def get_user_preferences(
    brand_id: UUID,
    session: Annotated[AsyncSession, Depends(get_async_session)],
    user_id: UUID | None = Query(None, description="User ID to analyze"),
) -> UserPreferenceResponse:
    """Analyze user preferences.

    Args:
        brand_id: Brand UUID
        session: Database session
        user_id: Optional user ID to analyze

    Returns:
        UserPreferenceResponse: Analyzed user preferences

    Raises:
        HTTPException: If brand not found
    """
    # Verify brand exists
    brand_repository = BrandRepositoryImpl(session)
    brand = await brand_repository.get_by_id(brand_id)

    if brand is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Brand not found: {brand_id}",
        )

    # Get AI analysis
    ai_service = get_ai_service(session=session)
    result = await ai_service.analyze_user_preferences(
        brand_id=brand_id,
        user_id=user_id,
    )

    # Convert to response schema
    return UserPreferenceResponse(
        user_id=result.user_id,
        preferred_categories=result.preferred_categories,
        preferred_price_range=result.preferred_price_range,
        dietary_preferences=result.dietary_preferences,
        order_frequency=result.order_frequency,
    )
