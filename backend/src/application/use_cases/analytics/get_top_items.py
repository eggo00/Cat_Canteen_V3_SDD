"""
GetTopItems Use Case

Retrieves top-selling menu items for a brand within a date range.
"""

from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal
from uuid import UUID

from src.domain.repositories.brand_repository import BrandRepository
from src.domain.repositories.order_repository import OrderRepository
from src.domain.value_objects.order_status import OrderStatus


@dataclass
class TopItemDTO:
    """Top item data transfer object."""

    menu_item_id: str | None
    menu_item_name: str
    quantity_sold: int
    total_revenue: Decimal
    percentage_of_total: float
    rank: int


class GetTopItems:
    """Use case for retrieving top-selling items.

    Analyzes order data to identify the best-selling menu items
    by quantity and revenue for a brand within a specified date range.
    """

    # Statuses that count for sales analysis
    SALES_STATUSES = {
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
        limit: int = 10,
    ) -> list[TopItemDTO]:
        """Execute the get top items use case.

        Args:
            brand_id: Brand identifier
            start_date: Start of date range (default: 30 days ago)
            end_date: End of date range (default: today)
            limit: Maximum number of items to return (default: 10)

        Returns:
            list[TopItemDTO]: Top-selling items ranked by quantity

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

        # Validate limit
        if limit < 1:
            raise ValueError("Limit must be at least 1")
        if limit > 100:
            limit = 100  # Cap at 100 to prevent excessive queries

        # Get top items from repository
        top_items_data = await self._order_repo.get_top_items_by_date_range(
            brand_id=brand_id,
            start_date=start_date,
            end_date=end_date,
            statuses=list(self.SALES_STATUSES),
            limit=limit,
        )

        # Calculate total quantity for percentage
        total_quantity = sum(item["quantity_sold"] for item in top_items_data)

        # Transform to DTOs with ranking
        top_items = []
        for rank, item in enumerate(top_items_data, start=1):
            percentage = (
                (item["quantity_sold"] / total_quantity * 100)
                if total_quantity > 0
                else 0.0
            )
            top_items.append(TopItemDTO(
                menu_item_id=str(item["menu_item_id"]) if item["menu_item_id"] else None,
                menu_item_name=item["menu_item_name"],
                quantity_sold=item["quantity_sold"],
                total_revenue=Decimal(str(item["total_revenue"])),
                percentage_of_total=round(percentage, 2),
                rank=rank,
            ))

        return top_items
