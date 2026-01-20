"""CreateOrder Use Case - Application Layer.

Handles the creation of new orders.
"""

from decimal import Decimal
from uuid import UUID

from src.domain.entities.order import Order
from src.domain.exceptions import NotFoundError, ValidationError
from src.domain.repositories.brand_repository import BrandRepository
from src.domain.repositories.menu_repository import MenuRepository
from src.domain.repositories.order_repository import OrderRepository
from src.domain.services.order_service import OrderService


class CreateOrder:
    """Use case for creating a new order.

    Validates order data, verifies menu items exist,
    and persists the order.
    """

    def __init__(
        self,
        order_repository: OrderRepository,
        brand_repository: BrandRepository,
        menu_repository: MenuRepository,
        order_service: OrderService,
    ):
        """Initialize the use case.

        Args:
            order_repository: Repository for order persistence
            brand_repository: Repository for brand data
            menu_repository: Repository for menu data
            order_service: Domain service for order operations
        """
        self.order_repository = order_repository
        self.brand_repository = brand_repository
        self.menu_repository = menu_repository
        self.order_service = order_service

    async def execute(self, data: dict) -> Order:
        """Execute the create order use case.

        Args:
            data: Order data containing:
                - brand_id: UUID of the brand
                - customer_name: Customer name
                - customer_phone: Customer phone number
                - items: List of order items with:
                    - menu_item_id: UUID of the menu item
                    - quantity: Number of items
                    - customizations: Optional list of customizations
                    - notes: Optional item notes
                - notes: Optional order-level notes

        Returns:
            Order: Created order entity

        Raises:
            NotFoundError: If brand or menu items not found
            ValidationError: If validation fails
        """
        # Extract and validate brand_id
        brand_id = data.get("brand_id")
        if not brand_id:
            raise ValidationError("Brand ID is required")

        if isinstance(brand_id, str):
            brand_id = UUID(brand_id)

        # Verify brand exists and is active
        brand = await self.brand_repository.get_by_id(brand_id)
        if not brand:
            raise NotFoundError(f"Brand not found: {brand_id}")

        if not brand.is_active:
            raise ValidationError(f"Brand is not active: {brand.name}")

        # Extract items data
        items_data = data.get("items", [])
        if not items_data:
            raise ValidationError("Order must have at least one item")

        # Create order items with menu item validation
        order_items = []
        for item_data in items_data:
            menu_item_id = item_data.get("menu_item_id")
            if not menu_item_id:
                raise ValidationError("Menu item ID is required for each item")

            if isinstance(menu_item_id, str):
                menu_item_id = UUID(menu_item_id)

            # Get menu item to verify it exists and get current price/name
            menu_item = await self.menu_repository.get_menu_item_by_id(menu_item_id)
            if not menu_item:
                raise NotFoundError(f"Menu item not found: {menu_item_id}")

            if not menu_item.is_available:
                raise ValidationError(f"Menu item is not available: {menu_item.name}")

            # Create order item
            quantity = item_data.get("quantity", 1)
            order_item = self.order_service.create_order_item(
                menu_item_id=menu_item_id,
                menu_item_name=menu_item.name,
                quantity=quantity,
                unit_price=Decimal(str(menu_item.price)),
                customizations=item_data.get("customizations"),
                notes=item_data.get("notes"),
            )
            order_items.append(order_item)

        # Create order entity
        order = Order(
            brand_id=brand_id,
            customer_name=data.get("customer_name"),
            customer_phone=data.get("customer_phone"),
            items=order_items,
            notes=data.get("notes"),
        )

        # Validate order
        validation_errors = self.order_service.validate_order(order)
        if validation_errors:
            raise ValidationError("; ".join(validation_errors))

        # Persist order
        created_order = await self.order_repository.create(order)

        return created_order
