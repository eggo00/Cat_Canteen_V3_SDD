"""
GetOrdersByHour Use Case

Retrieves hourly order distribution for a brand within a date range.
"""

from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal
from uuid import UUID

from src.domain.repositories.order_repository import OrderRepository
from src.domain.repositories.brand_repository import BrandRepository
from src.domain.value_objects.order_status import OrderStatus


@dataclass
class HourlyOrdersDTO:
    """Hourly orders data transfer object."""

    hour: int  # 0-23
    order_count: int
    total_revenue: Decimal
    average_order_value: Decimal
    percentage_of_total: float


class GetOrdersByHour:
    """Use case for retrieving hourly order distribution.

    Analyzes order patterns by hour of day to help identify
    peak ordering times and optimize staffing.
    """

    # All non-cancelled statuses count for distribution analysis
    ANALYSIS_STATUSES = {
        OrderStatus.PENDING,
        OrderStatus.CONFIRMED,
        OrderStatus.PREPARING,
        OrderStatus.READY,
        OrderStatus.COMPLETED,
    }

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
    ) -> list[HourlyOrdersDTO]:
        """Execute the get orders by hour use case.

        Args:
            brand_id: Brand identifier
            start_date: Start of date range (default: 7 days ago)
            end_date: End of date range (default: today)

        Returns:
            list[HourlyOrdersDTO]: Hourly order distribution (24 items, 0-23)

        Raises:
            ValueError: If brand not found or date range is invalid
        """
        # Verify brand exists
        brand = await self._brand_repo.get_by_id(brand_id)
        if not brand:
            raise ValueError(f"Brand with ID {brand_id} not found")

        # Set default date range (last 7 days for hourly patterns)
        today = date.today()
        if end_date is None:
            end_date = today
        if start_date is None:
            start_date = end_date - timedelta(days=7)

        # Validate date range
        if start_date > end_date:
            raise ValueError("Start date must be before or equal to end date")

        # Get hourly data from repository
        hourly_data = await self._order_repo.get_orders_by_hour(
            brand_id=brand_id,
            start_date=start_date,
            end_date=end_date,
            statuses=list(self.ANALYSIS_STATUSES),
        )

        # Create a dict for quick lookup
        data_by_hour = {item["hour"]: item for item in hourly_data}

        # Calculate totals
        total_orders = sum(item["order_count"] for item in hourly_data)

        # Build complete hourly breakdown (0-23)
        result = []
        for hour in range(24):
            if hour in data_by_hour:
                item = data_by_hour[hour]
                order_count = item["order_count"]
                total_revenue = Decimal(str(item["total_revenue"]))
                avg_value = total_revenue / order_count if order_count > 0 else Decimal("0")
                percentage = (order_count / total_orders * 100) if total_orders > 0 else 0.0
            else:
                order_count = 0
                total_revenue = Decimal("0")
                avg_value = Decimal("0")
                percentage = 0.0

            result.append(HourlyOrdersDTO(
                hour=hour,
                order_count=order_count,
                total_revenue=total_revenue,
                average_order_value=avg_value,
                percentage_of_total=round(percentage, 2),
            ))

        return result
