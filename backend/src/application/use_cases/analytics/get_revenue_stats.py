"""
GetRevenueStats Use Case

Retrieves revenue statistics for a brand within a date range.
"""

from dataclasses import dataclass
from datetime import date, datetime, timedelta
from decimal import Decimal
from uuid import UUID

from src.domain.repositories.order_repository import OrderRepository
from src.domain.repositories.brand_repository import BrandRepository
from src.domain.value_objects.order_status import OrderStatus


@dataclass
class DailyRevenueDTO:
    """Daily revenue data transfer object."""

    date: date
    total_revenue: Decimal
    order_count: int
    average_order_value: Decimal


@dataclass
class RevenueStatsDTO:
    """Revenue statistics data transfer object."""

    brand_id: str
    start_date: date
    end_date: date
    total_revenue: Decimal
    total_orders: int
    average_order_value: Decimal
    daily_revenue: list[DailyRevenueDTO]
    revenue_change_percentage: float | None  # Compared to previous period


class GetRevenueStats:
    """Use case for retrieving revenue statistics.

    Calculates total revenue, daily breakdown, and trends
    for a brand within a specified date range.
    """

    # Statuses that count as revenue (completed orders)
    REVENUE_STATUSES = {OrderStatus.COMPLETED, OrderStatus.READY}

    def __init__(
        self,
        order_repository: OrderRepository,
        brand_repository: BrandRepository,
    ):
        self._order_repo = order_repository
        self._brand_repo = brand_repository

    async def execute(
        self,
        brand_id: UUID,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> RevenueStatsDTO:
        """Execute the get revenue stats use case.

        Args:
            brand_id: Brand identifier
            start_date: Start of date range (default: 30 days ago)
            end_date: End of date range (default: today)

        Returns:
            RevenueStatsDTO: Revenue statistics for the period

        Raises:
            ValueError: If brand not found or date range is invalid
        """
        # Verify brand exists
        brand = await self._brand_repo.get_by_id(brand_id)
        if not brand:
            raise ValueError(f"Brand with ID {brand_id} not found")

        # Set default date range (last 30 days)
        today = date.today()
        if end_date is None:
            end_date = today
        if start_date is None:
            start_date = end_date - timedelta(days=30)

        # Validate date range
        if start_date > end_date:
            raise ValueError("Start date must be before or equal to end date")

        # Get revenue data from repository
        revenue_data = await self._order_repo.get_revenue_by_date_range(
            brand_id=brand_id,
            start_date=start_date,
            end_date=end_date,
            statuses=list(self.REVENUE_STATUSES),
        )

        # Calculate daily breakdown
        daily_revenue = []
        total_revenue = Decimal("0")
        total_orders = 0

        # Create a dict for quick lookup
        revenue_by_date = {
            item["date"]: item for item in revenue_data
        }

        # Fill in all dates in range (including days with no orders)
        current_date = start_date
        while current_date <= end_date:
            if current_date in revenue_by_date:
                item = revenue_by_date[current_date]
                day_revenue = Decimal(str(item["revenue"]))
                day_orders = item["order_count"]
                avg_value = day_revenue / day_orders if day_orders > 0 else Decimal("0")
            else:
                day_revenue = Decimal("0")
                day_orders = 0
                avg_value = Decimal("0")

            daily_revenue.append(DailyRevenueDTO(
                date=current_date,
                total_revenue=day_revenue,
                order_count=day_orders,
                average_order_value=avg_value,
            ))

            total_revenue += day_revenue
            total_orders += day_orders
            current_date += timedelta(days=1)

        # Calculate average order value
        average_order_value = (
            total_revenue / total_orders if total_orders > 0 else Decimal("0")
        )

        # Calculate revenue change compared to previous period
        revenue_change = await self._calculate_revenue_change(
            brand_id=brand_id,
            current_revenue=total_revenue,
            start_date=start_date,
            end_date=end_date,
        )

        return RevenueStatsDTO(
            brand_id=str(brand_id),
            start_date=start_date,
            end_date=end_date,
            total_revenue=total_revenue,
            total_orders=total_orders,
            average_order_value=average_order_value,
            daily_revenue=daily_revenue,
            revenue_change_percentage=revenue_change,
        )

    async def _calculate_revenue_change(
        self,
        brand_id: UUID,
        current_revenue: Decimal,
        start_date: date,
        end_date: date,
    ) -> float | None:
        """Calculate percentage change compared to previous period.

        Args:
            brand_id: Brand identifier
            current_revenue: Current period revenue
            start_date: Current period start date
            end_date: Current period end date

        Returns:
            float | None: Percentage change or None if no previous data
        """
        # Calculate previous period dates
        period_days = (end_date - start_date).days + 1
        prev_end_date = start_date - timedelta(days=1)
        prev_start_date = prev_end_date - timedelta(days=period_days - 1)

        # Get previous period revenue
        prev_data = await self._order_repo.get_revenue_by_date_range(
            brand_id=brand_id,
            start_date=prev_start_date,
            end_date=prev_end_date,
            statuses=list(self.REVENUE_STATUSES),
        )

        prev_revenue = sum(
            Decimal(str(item["revenue"])) for item in prev_data
        )

        if prev_revenue == 0:
            return None

        change = ((current_revenue - prev_revenue) / prev_revenue) * 100
        return float(change)
