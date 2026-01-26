"""AI API routes.

Provides endpoints for AI-powered recommendations and predictions.
Currently uses stub implementation; will be replaced with real ML models.

Performance requirement: Response time ≤ 500ms (SC-009)
"""
import base64
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.v1.schemas.ai_schemas import (
    AIStatusResponse,
    DemandForecastResponse,
    DemandPredictionItem,
    RecommendationItemResponse,
    RecommendationResponse,
    UserPreferenceResponse,
)
from src.api.v1.schemas.menu_extract_schemas import (
    MenuDraft,
    MenuDraftCategory,
    MenuDraftItem,
    MenuExtractResponse,
)
from src.infrastructure.ai.ai_service_stub import AIServiceStub, get_ai_service
from src.infrastructure.ai.menu_extractor import get_menu_extractor
from src.infrastructure.ai.rate_limiter import get_rate_limiter
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


# ============================================================================
# Menu Extraction Endpoints (Phase I - AI Recognition)
# ============================================================================


@router.post(
    "/menu/extract",
    response_model=MenuDraft,
    summary="Extract menu from image using AI",
    description="Upload a menu image and use AI to extract menu items. Returns a MenuDraft for human review.",
)
async def extract_menu_from_image(
    session: Annotated[AsyncSession, Depends(get_async_session)],
    image: UploadFile = File(..., description="Menu image to extract (JPEG, PNG, WebP)"),
    brand_id: str = Form(..., description="Brand ID for the menu"),
    user_id: str = Form(..., description="User ID for rate limiting"),
) -> MenuDraft:
    """Extract menu items from an uploaded image using AI.

    This endpoint uses Claude Vision API to recognize menu items from images.
    The result is returned as a MenuDraft that requires human confirmation
    before being saved to the official menu.

    Rate limits apply:
    - Per-brand: 50 requests/day
    - Per-user: 10 requests/hour
    - Global: 30 requests/minute

    Args:
        session: Database session
        image: Uploaded menu image file
        brand_id: Brand identifier
        user_id: User identifier for rate limiting

    Returns:
        MenuDraft: Extracted menu data pending human review

    Raises:
        HTTPException 400: Invalid image format
        HTTPException 404: Brand not found
        HTTPException 429: Rate limit exceeded
        HTTPException 500: AI service error
    """
    # Validate brand exists
    brand_repository = BrandRepositoryImpl(session)
    brand = await brand_repository.get_by_id(UUID(brand_id))

    if brand is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Brand not found: {brand_id}",
        )

    # Check rate limits
    rate_limiter = get_rate_limiter()
    allowed, error_message = rate_limiter.check_and_consume(brand_id, user_id)

    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=error_message,
        )

    # Validate image type
    if image.content_type not in ["image/jpeg", "image/png", "image/webp"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"不支援的圖片格式：{image.content_type}。請上傳 JPEG、PNG 或 WebP 圖片。",
        )

    # Read and encode image
    try:
        image_content = await image.read()
        image_base64 = base64.b64encode(image_content).decode("utf-8")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"無法讀取圖片：{str(e)}",
        )

    # Get menu extractor and extract
    try:
        extractor = get_menu_extractor()
        result = await extractor.extract(image_base64)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )

    # Check for extraction errors
    if not result.success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result.error_message or "AI 辨識失敗",
        )

    # Convert to MenuDraft
    draft_categories = []
    for cat in result.categories:
        draft_items = []
        for item in cat.items:
            needs_review = item.price == 0
            draft_items.append(
                MenuDraftItem(
                    name=item.name,
                    price=item.price,
                    description=item.description,
                    needs_review=needs_review,
                    review_reason="價格為 0，請確認" if needs_review else None,
                )
            )
        draft_categories.append(
            MenuDraftCategory(
                name=cat.name,
                items=draft_items,
            )
        )

    return MenuDraft(
        source="ai_extract",
        brand_id=brand_id,
        categories=draft_categories,
        warnings=result.warnings,
        stats=result.stats,
        raw_text=result.raw_text,
    )


@router.get(
    "/menu/extract/quota",
    summary="Get AI extraction quota",
    description="Get remaining AI extraction quota for brand and user",
)
async def get_extraction_quota(
    brand_id: str = Query(..., description="Brand ID"),
    user_id: str = Query(..., description="User ID"),
) -> dict:
    """Get remaining AI extraction quota.

    Args:
        brand_id: Brand identifier
        user_id: User identifier

    Returns:
        Dict with remaining quota information
    """
    rate_limiter = get_rate_limiter()
    return rate_limiter.get_remaining_quota(brand_id, user_id)
