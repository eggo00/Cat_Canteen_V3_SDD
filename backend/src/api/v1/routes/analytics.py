"""
Analytics API Routes

REST endpoints for analytics and reporting.
"""

from datetime import date, timedelta
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.v1.schemas.analytics_schemas import (
    AnalyticsSummaryResponse,
    DailyRevenueResponse,
    HourlyDistributionResponse,
    HourlyOrdersResponse,
    ReportTypeEnum,
    RevenueStatsResponse,
    TopItemResponse,
    TopItemsResponse,
)
from src.application.use_cases.analytics import (
    ExportReport,
    GetOrdersByHour,
    GetRevenueStats,
    GetTopItems,
    ReportFormat,
)
from src.application.use_cases.analytics.export_report import ReportType
from src.domain.repositories.brand_repository import BrandRepository
from src.domain.repositories.order_repository import OrderRepository
from src.infrastructure.database.session import get_async_session
from src.infrastructure.repositories.brand_repository_impl import BrandRepositoryImpl
from src.infrastructure.repositories.order_repository_impl import OrderRepositoryImpl

router = APIRouter(prefix="/analytics", tags=["analytics"])


# ==================== Dependencies ====================


async def get_order_repository(
    session: AsyncSession = Depends(get_async_session),
) -> OrderRepository:
    """Get order repository dependency."""
    return OrderRepositoryImpl(session)


async def get_brand_repository(
    session: AsyncSession = Depends(get_async_session),
) -> BrandRepository:
    """Get brand repository dependency."""
    return BrandRepositoryImpl(session)


# ==================== Revenue Endpoints ====================


@router.get(
    "/brands/{brand_id}/revenue",
    response_model=RevenueStatsResponse,
    summary="Get revenue statistics",
    description="Get revenue statistics for a brand within a date range.",
)
async def get_revenue_stats(
    brand_id: UUID,
    start_date: date | None = Query(
        None, description="Start date (default: 30 days ago)"
    ),
    end_date: date | None = Query(None, description="End date (default: today)"),
    order_repo: OrderRepository = Depends(get_order_repository),
    brand_repo: BrandRepository = Depends(get_brand_repository),
) -> RevenueStatsResponse:
    """Get revenue statistics for a brand.

    Returns daily revenue breakdown, totals, and comparison with previous period.
    """
    try:
        use_case = GetRevenueStats(order_repo, brand_repo)
        result = await use_case.execute(brand_id, start_date, end_date)

        return RevenueStatsResponse(
            brand_id=result.brand_id,
            start_date=result.start_date,
            end_date=result.end_date,
            total_revenue=result.total_revenue,
            total_orders=result.total_orders,
            average_order_value=result.average_order_value,
            daily_revenue=[
                DailyRevenueResponse(
                    report_date=day.date,
                    total_revenue=day.total_revenue,
                    order_count=day.order_count,
                    average_order_value=day.average_order_value,
                )
                for day in result.daily_revenue
            ],
            revenue_change_percentage=result.revenue_change_percentage,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


# ==================== Top Items Endpoints ====================


@router.get(
    "/brands/{brand_id}/top-items",
    response_model=TopItemsResponse,
    summary="Get top selling items",
    description="Get top selling menu items ranked by quantity sold.",
)
async def get_top_items(
    brand_id: UUID,
    start_date: date | None = Query(
        None, description="Start date (default: 30 days ago)"
    ),
    end_date: date | None = Query(None, description="End date (default: today)"),
    limit: int = Query(10, ge=1, le=100, description="Number of items to return"),
    order_repo: OrderRepository = Depends(get_order_repository),
    brand_repo: BrandRepository = Depends(get_brand_repository),
) -> TopItemsResponse:
    """Get top selling items for a brand.

    Returns items ranked by quantity sold with revenue contribution.
    """
    try:
        use_case = GetTopItems(order_repo, brand_repo)
        result = await use_case.execute(brand_id, start_date, end_date, limit)

        # Determine actual date range used
        today = date.today()
        actual_end = end_date or today
        actual_start = start_date or (actual_end - timedelta(days=30))

        return TopItemsResponse(
            brand_id=str(brand_id),
            start_date=actual_start,
            end_date=actual_end,
            items=[
                TopItemResponse(
                    menu_item_id=item.menu_item_id,
                    menu_item_name=item.menu_item_name,
                    quantity_sold=item.quantity_sold,
                    total_revenue=item.total_revenue,
                    percentage_of_total=item.percentage_of_total,
                    rank=item.rank,
                )
                for item in result
            ],
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


# ==================== Hourly Distribution Endpoints ====================


@router.get(
    "/brands/{brand_id}/orders-by-hour",
    response_model=HourlyDistributionResponse,
    summary="Get hourly order distribution",
    description="Get order distribution by hour of day.",
)
async def get_orders_by_hour(
    brand_id: UUID,
    start_date: date | None = Query(
        None, description="Start date (default: 7 days ago)"
    ),
    end_date: date | None = Query(None, description="End date (default: today)"),
    order_repo: OrderRepository = Depends(get_order_repository),
    brand_repo: BrandRepository = Depends(get_brand_repository),
) -> HourlyDistributionResponse:
    """Get hourly order distribution for a brand.

    Returns order counts and revenue by hour of day (0-23).
    """
    try:
        use_case = GetOrdersByHour(order_repo, brand_repo)
        result = await use_case.execute(brand_id, start_date, end_date)

        # Determine actual date range used
        today = date.today()
        actual_end = end_date or today
        actual_start = start_date or (actual_end - timedelta(days=7))

        # Find peak hour
        peak_hour = None
        peak_orders = 0
        for hour_data in result:
            if hour_data.order_count > peak_orders:
                peak_orders = hour_data.order_count
                peak_hour = hour_data.hour

        return HourlyDistributionResponse(
            brand_id=str(brand_id),
            start_date=actual_start,
            end_date=actual_end,
            hourly_data=[
                HourlyOrdersResponse(
                    hour=h.hour,
                    order_count=h.order_count,
                    total_revenue=h.total_revenue,
                    average_order_value=h.average_order_value,
                    percentage_of_total=h.percentage_of_total,
                )
                for h in result
            ],
            peak_hour=peak_hour,
            peak_hour_orders=peak_orders if peak_orders > 0 else None,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


# ==================== Summary Endpoint ====================


@router.get(
    "/brands/{brand_id}/summary",
    response_model=AnalyticsSummaryResponse,
    summary="Get analytics summary",
    description="Get a combined analytics summary for the dashboard.",
)
async def get_analytics_summary(
    brand_id: UUID,
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    order_repo: OrderRepository = Depends(get_order_repository),
    brand_repo: BrandRepository = Depends(get_brand_repository),
) -> AnalyticsSummaryResponse:
    """Get combined analytics summary for a brand.

    Returns revenue, top items, and peak hours in one response.
    """
    try:
        today = date.today()
        start_date = today - timedelta(days=days)
        end_date = today

        # Get all data in parallel (logically, but sequential for simplicity)
        revenue_uc = GetRevenueStats(order_repo, brand_repo)
        top_items_uc = GetTopItems(order_repo, brand_repo)
        hourly_uc = GetOrdersByHour(order_repo, brand_repo)

        revenue = await revenue_uc.execute(brand_id, start_date, end_date)
        top_items = await top_items_uc.execute(brand_id, start_date, end_date, limit=5)
        hourly = await hourly_uc.execute(brand_id, start_date, end_date)

        # Find peak hour
        peak_hour = None
        peak_orders = 0
        for h in hourly:
            if h.order_count > peak_orders:
                peak_orders = h.order_count
                peak_hour = h.hour

        return AnalyticsSummaryResponse(
            brand_id=str(brand_id),
            period=f"Last {days} days",
            total_revenue=revenue.total_revenue,
            total_orders=revenue.total_orders,
            average_order_value=revenue.average_order_value,
            revenue_change=revenue.revenue_change_percentage,
            top_items=[
                TopItemResponse(
                    menu_item_id=item.menu_item_id,
                    menu_item_name=item.menu_item_name,
                    quantity_sold=item.quantity_sold,
                    total_revenue=item.total_revenue,
                    percentage_of_total=item.percentage_of_total,
                    rank=item.rank,
                )
                for item in top_items
            ],
            peak_hour=peak_hour,
            peak_hour_orders=peak_orders if peak_orders > 0 else None,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


# ==================== Export Endpoint ====================


@router.get(
    "/brands/{brand_id}/export/{report_type}",
    summary="Export analytics report",
    description="Export analytics data as CSV file.",
)
async def export_report(
    brand_id: UUID,
    report_type: ReportTypeEnum,
    start_date: date | None = Query(
        None, description="Start date (default: 30 days ago)"
    ),
    end_date: date | None = Query(None, description="End date (default: today)"),
    order_repo: OrderRepository = Depends(get_order_repository),
    brand_repo: BrandRepository = Depends(get_brand_repository),
) -> Response:
    """Export analytics report as CSV.

    Returns a downloadable CSV file with the requested data.
    """
    try:
        # Create use cases
        revenue_uc = GetRevenueStats(order_repo, brand_repo)
        top_items_uc = GetTopItems(order_repo, brand_repo)
        hourly_uc = GetOrdersByHour(order_repo, brand_repo)

        export_uc = ExportReport(revenue_uc, top_items_uc, hourly_uc)

        # Map API enum to internal enum
        type_mapping = {
            ReportTypeEnum.REVENUE: ReportType.REVENUE,
            ReportTypeEnum.TOP_ITEMS: ReportType.TOP_ITEMS,
            ReportTypeEnum.HOURLY: ReportType.HOURLY,
            ReportTypeEnum.SUMMARY: ReportType.SUMMARY,
        }

        result = await export_uc.execute(
            brand_id=brand_id,
            report_type=type_mapping[report_type],
            start_date=start_date,
            end_date=end_date,
            format=ReportFormat.CSV,
        )

        # Add BOM for proper UTF-8 handling in Excel
        content_with_bom = "\ufeff" + result.content

        return Response(
            content=content_with_bom.encode("utf-8"),
            media_type=result.content_type,
            headers={
                "Content-Disposition": f'attachment; filename="{result.filename}"',
            },
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
