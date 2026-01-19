"""
Analytics API Schemas

Pydantic models for analytics request/response validation.
"""

from datetime import date as date_type
from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class ReportTypeEnum(str, Enum):
    """Report types for export."""

    REVENUE = "revenue"
    TOP_ITEMS = "top_items"
    HOURLY = "hourly"
    SUMMARY = "summary"


# ==================== Revenue Statistics ====================


class DailyRevenueResponse(BaseModel):
    """Daily revenue data."""

    model_config = ConfigDict(populate_by_name=True)

    report_date: date_type = Field(..., description="Date", serialization_alias="date")
    total_revenue: Decimal = Field(..., description="Total revenue for the day")
    order_count: int = Field(..., description="Number of orders")
    average_order_value: Decimal = Field(..., description="Average order value")


class RevenueStatsResponse(BaseModel):
    """Revenue statistics response."""

    brand_id: str = Field(..., description="Brand ID")
    start_date: date_type = Field(..., description="Start date of the period")
    end_date: date_type = Field(..., description="End date of the period")
    total_revenue: Decimal = Field(..., description="Total revenue for the period")
    total_orders: int = Field(..., description="Total number of orders")
    average_order_value: Decimal = Field(..., description="Average order value")
    daily_revenue: list[DailyRevenueResponse] = Field(
        ..., description="Daily breakdown of revenue"
    )
    revenue_change_percentage: float | None = Field(
        None, description="Percentage change compared to previous period"
    )


# ==================== Top Items ====================


class TopItemResponse(BaseModel):
    """Top selling item data."""

    menu_item_id: str | None = Field(None, description="Menu item ID")
    menu_item_name: str = Field(..., description="Name of the menu item")
    quantity_sold: int = Field(..., description="Total quantity sold")
    total_revenue: Decimal = Field(..., description="Total revenue from this item")
    percentage_of_total: float = Field(
        ..., description="Percentage of total sales volume"
    )
    rank: int = Field(..., description="Ranking position")


class TopItemsResponse(BaseModel):
    """Top items list response."""

    brand_id: str = Field(..., description="Brand ID")
    start_date: date_type = Field(..., description="Start date of the period")
    end_date: date_type = Field(..., description="End date of the period")
    items: list[TopItemResponse] = Field(..., description="Top selling items")


# ==================== Hourly Distribution ====================


class HourlyOrdersResponse(BaseModel):
    """Hourly order distribution data."""

    hour: int = Field(..., ge=0, le=23, description="Hour of day (0-23)")
    order_count: int = Field(..., description="Number of orders in this hour")
    total_revenue: Decimal = Field(..., description="Total revenue in this hour")
    average_order_value: Decimal = Field(..., description="Average order value")
    percentage_of_total: float = Field(
        ..., description="Percentage of total orders"
    )


class HourlyDistributionResponse(BaseModel):
    """Hourly distribution response."""

    brand_id: str = Field(..., description="Brand ID")
    start_date: date_type = Field(..., description="Start date of the period")
    end_date: date_type = Field(..., description="End date of the period")
    hourly_data: list[HourlyOrdersResponse] = Field(
        ..., description="Hourly order distribution"
    )
    peak_hour: int | None = Field(None, description="Hour with most orders")
    peak_hour_orders: int | None = Field(
        None, description="Number of orders in peak hour"
    )


# ==================== Export ====================


class ExportRequest(BaseModel):
    """Export report request."""

    report_type: ReportTypeEnum = Field(..., description="Type of report to export")
    start_date: date_type | None = Field(None, description="Start date")
    end_date: date_type | None = Field(None, description="End date")


# ==================== Analytics Summary ====================


class AnalyticsSummaryResponse(BaseModel):
    """Combined analytics summary for dashboard."""

    brand_id: str = Field(..., description="Brand ID")
    period: str = Field(..., description="Period description (e.g., 'Last 30 days')")

    # Revenue summary
    total_revenue: Decimal = Field(..., description="Total revenue")
    total_orders: int = Field(..., description="Total orders")
    average_order_value: Decimal = Field(..., description="Average order value")
    revenue_change: float | None = Field(
        None, description="Revenue change vs previous period"
    )

    # Top items preview (top 5)
    top_items: list[TopItemResponse] = Field(
        ..., description="Top 5 selling items"
    )

    # Peak hours info
    peak_hour: int | None = Field(None, description="Peak ordering hour")
    peak_hour_orders: int | None = Field(None, description="Orders in peak hour")
