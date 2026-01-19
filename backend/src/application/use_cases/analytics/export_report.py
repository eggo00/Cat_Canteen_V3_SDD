"""
ExportReport Use Case

Generates exportable reports (CSV) for analytics data.
"""

import csv
import io
from dataclasses import dataclass
from datetime import date, timedelta
from enum import Enum
from uuid import UUID

from .get_revenue_stats import GetRevenueStats
from .get_top_items import GetTopItems
from .get_orders_by_hour import GetOrdersByHour


class ReportFormat(str, Enum):
    """Supported export formats."""

    CSV = "csv"


class ReportType(str, Enum):
    """Types of reports available."""

    REVENUE = "revenue"
    TOP_ITEMS = "top_items"
    HOURLY = "hourly"
    SUMMARY = "summary"


@dataclass
class ExportResult:
    """Export result data transfer object."""

    content: str
    filename: str
    content_type: str


class ExportReport:
    """Use case for exporting analytics reports.

    Generates downloadable reports in various formats
    for different types of analytics data.
    """

    def __init__(
        self,
        get_revenue_stats: GetRevenueStats,
        get_top_items: GetTopItems,
        get_orders_by_hour: GetOrdersByHour,
    ):
        self._revenue_stats = get_revenue_stats
        self._top_items = get_top_items
        self._orders_by_hour = get_orders_by_hour

    async def execute(
        self,
        brand_id: UUID,
        report_type: ReportType,
        start_date: date | None = None,
        end_date: date | None = None,
        format: ReportFormat = ReportFormat.CSV,
    ) -> ExportResult:
        """Execute the export report use case.

        Args:
            brand_id: Brand identifier
            report_type: Type of report to generate
            start_date: Start of date range
            end_date: End of date range
            format: Export format (default: CSV)

        Returns:
            ExportResult: Generated report content and metadata

        Raises:
            ValueError: If parameters are invalid
        """
        # Set default dates
        today = date.today()
        if end_date is None:
            end_date = today
        if start_date is None:
            start_date = end_date - timedelta(days=30)

        # Generate report based on type
        if report_type == ReportType.REVENUE:
            return await self._export_revenue(brand_id, start_date, end_date)
        elif report_type == ReportType.TOP_ITEMS:
            return await self._export_top_items(brand_id, start_date, end_date)
        elif report_type == ReportType.HOURLY:
            return await self._export_hourly(brand_id, start_date, end_date)
        elif report_type == ReportType.SUMMARY:
            return await self._export_summary(brand_id, start_date, end_date)
        else:
            raise ValueError(f"Unknown report type: {report_type}")

    async def _export_revenue(
        self,
        brand_id: UUID,
        start_date: date,
        end_date: date,
    ) -> ExportResult:
        """Export daily revenue report."""
        stats = await self._revenue_stats.execute(brand_id, start_date, end_date)

        output = io.StringIO()
        writer = csv.writer(output)

        # Header
        writer.writerow([
            "日期",
            "營收 (NT$)",
            "訂單數",
            "平均客單價 (NT$)",
        ])

        # Data rows
        for day in stats.daily_revenue:
            writer.writerow([
                day.date.isoformat(),
                f"{day.total_revenue:.0f}",
                day.order_count,
                f"{day.average_order_value:.0f}",
            ])

        # Summary row
        writer.writerow([])
        writer.writerow([
            "總計",
            f"{stats.total_revenue:.0f}",
            stats.total_orders,
            f"{stats.average_order_value:.0f}",
        ])

        return ExportResult(
            content=output.getvalue(),
            filename=f"revenue_{start_date}_{end_date}.csv",
            content_type="text/csv; charset=utf-8",
        )

    async def _export_top_items(
        self,
        brand_id: UUID,
        start_date: date,
        end_date: date,
    ) -> ExportResult:
        """Export top items report."""
        top_items = await self._top_items.execute(brand_id, start_date, end_date)

        output = io.StringIO()
        writer = csv.writer(output)

        # Header
        writer.writerow([
            "排名",
            "品項名稱",
            "銷售數量",
            "營收 (NT$)",
            "佔比 (%)",
        ])

        # Data rows
        for item in top_items:
            writer.writerow([
                item.rank,
                item.menu_item_name,
                item.quantity_sold,
                f"{item.total_revenue:.0f}",
                f"{item.percentage_of_total:.1f}",
            ])

        return ExportResult(
            content=output.getvalue(),
            filename=f"top_items_{start_date}_{end_date}.csv",
            content_type="text/csv; charset=utf-8",
        )

    async def _export_hourly(
        self,
        brand_id: UUID,
        start_date: date,
        end_date: date,
    ) -> ExportResult:
        """Export hourly distribution report."""
        hourly = await self._orders_by_hour.execute(brand_id, start_date, end_date)

        output = io.StringIO()
        writer = csv.writer(output)

        # Header
        writer.writerow([
            "時段",
            "訂單數",
            "營收 (NT$)",
            "平均客單價 (NT$)",
            "佔比 (%)",
        ])

        # Data rows
        for hour_data in hourly:
            writer.writerow([
                f"{hour_data.hour:02d}:00 - {hour_data.hour:02d}:59",
                hour_data.order_count,
                f"{hour_data.total_revenue:.0f}",
                f"{hour_data.average_order_value:.0f}",
                f"{hour_data.percentage_of_total:.1f}",
            ])

        return ExportResult(
            content=output.getvalue(),
            filename=f"hourly_{start_date}_{end_date}.csv",
            content_type="text/csv; charset=utf-8",
        )

    async def _export_summary(
        self,
        brand_id: UUID,
        start_date: date,
        end_date: date,
    ) -> ExportResult:
        """Export comprehensive summary report."""
        stats = await self._revenue_stats.execute(brand_id, start_date, end_date)
        top_items = await self._top_items.execute(brand_id, start_date, end_date, limit=10)
        hourly = await self._orders_by_hour.execute(brand_id, start_date, end_date)

        output = io.StringIO()
        writer = csv.writer(output)

        # Overview section
        writer.writerow(["=== 營運摘要報告 ==="])
        writer.writerow([f"期間: {start_date} 至 {end_date}"])
        writer.writerow([])

        # Revenue summary
        writer.writerow(["--- 營收概況 ---"])
        writer.writerow(["總營收 (NT$)", f"{stats.total_revenue:.0f}"])
        writer.writerow(["總訂單數", stats.total_orders])
        writer.writerow(["平均客單價 (NT$)", f"{stats.average_order_value:.0f}"])
        if stats.revenue_change_percentage is not None:
            writer.writerow(["與前期相比", f"{stats.revenue_change_percentage:+.1f}%"])
        writer.writerow([])

        # Top items section
        writer.writerow(["--- 熱銷品項 Top 10 ---"])
        writer.writerow(["排名", "品項", "數量", "營收"])
        for item in top_items[:10]:
            writer.writerow([
                item.rank,
                item.menu_item_name,
                item.quantity_sold,
                f"NT$ {item.total_revenue:.0f}",
            ])
        writer.writerow([])

        # Peak hours section
        writer.writerow(["--- 尖峰時段 ---"])
        # Find top 3 peak hours
        sorted_hours = sorted(hourly, key=lambda x: x.order_count, reverse=True)
        for hour_data in sorted_hours[:3]:
            if hour_data.order_count > 0:
                writer.writerow([
                    f"{hour_data.hour:02d}:00",
                    f"{hour_data.order_count} 筆訂單",
                    f"NT$ {hour_data.total_revenue:.0f}",
                ])

        return ExportResult(
            content=output.getvalue(),
            filename=f"summary_{start_date}_{end_date}.csv",
            content_type="text/csv; charset=utf-8",
        )
