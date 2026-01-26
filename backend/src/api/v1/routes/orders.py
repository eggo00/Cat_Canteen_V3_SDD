"""Order API Routes - REST endpoints for order operations."""

import logging
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.v1.schemas.order_schemas import (
    CreateOrderRequest,
    OrderItemResponse,
    OrderListResponse,
    OrderResponse,
    OrderStatusEnum,
    UpdateOrderStatusRequest,
)
from src.application.use_cases.create_order import CreateOrder
from src.application.use_cases.get_order import (
    GetActiveOrders,
    GetOrder,
    GetOrdersByBrand,
)
from src.application.use_cases.update_order_status import (
    CancelOrder,
    UpdateOrderStatus,
)
from src.domain.entities.order import Order
from src.domain.exceptions import NotFoundError, ValidationError
from src.domain.services.order_service import OrderService
from src.infrastructure.database.session import get_async_session
from src.infrastructure.repositories.brand_repository_impl import BrandRepositoryImpl
from src.infrastructure.repositories.menu_repository_impl import MenuRepositoryImpl
from src.infrastructure.repositories.order_repository_impl import OrderRepositoryImpl

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/orders", tags=["Orders"])


# Dependency to get order repository
async def get_order_repository(
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> OrderRepositoryImpl:
    """Get order repository instance."""
    return OrderRepositoryImpl(session)


# Dependency to get brand repository
async def get_brand_repository(
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> BrandRepositoryImpl:
    """Get brand repository instance."""
    return BrandRepositoryImpl(session)


# Dependency to get menu repository
async def get_menu_repository(
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> MenuRepositoryImpl:
    """Get menu repository instance."""
    return MenuRepositoryImpl(session)


def _to_response(order: Order) -> OrderResponse:
    """Convert Order entity to response schema."""
    return OrderResponse(
        id=order.id,
        brand_id=order.brand_id,
        order_number=order.order_number,
        customer_name=order.customer_name,
        customer_phone=order.customer_phone,
        items=[
            OrderItemResponse(
                id=item.id,
                menu_item_id=item.menu_item_id,
                menu_item_name=item.menu_item_name,
                quantity=item.quantity,
                unit_price=float(item.unit_price),
                subtotal=float(item.subtotal),
                customizations=item.customizations,
                notes=item.notes,
            )
            for item in order.items
        ],
        status=OrderStatusEnum(order.status.value),
        status_display=order.status.display_name,
        notes=order.notes,
        total=float(order.total),
        item_count=order.item_count,
        created_at=order.created_at,
        updated_at=order.updated_at,
    )


@router.post(
    "/brands/{brand_id}",
    response_model=OrderResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new order",
    description="Create a new order for a brand with customer and item information.",
)
async def create_order(
    brand_id: Annotated[UUID, Path(description="Brand ID")],
    request: CreateOrderRequest,
    order_repo: Annotated[OrderRepositoryImpl, Depends(get_order_repository)],
    brand_repo: Annotated[BrandRepositoryImpl, Depends(get_brand_repository)],
    menu_repo: Annotated[MenuRepositoryImpl, Depends(get_menu_repository)],
):
    """Create a new order."""
    try:
        # Initialize use case
        order_service = OrderService()
        use_case = CreateOrder(
            order_repository=order_repo,
            brand_repository=brand_repo,
            menu_repository=menu_repo,
            order_service=order_service,
        )

        # Prepare order data
        order_data = {
            "brand_id": brand_id,
            "customer_name": request.customer_name,
            "customer_phone": request.customer_phone,
            "items": [
                {
                    "menu_item_id": item.menu_item_id,
                    "quantity": item.quantity,
                    "customizations": [c.model_dump() for c in item.customizations]
                    if item.customizations
                    else None,
                    "notes": item.notes,
                }
                for item in request.items
            ],
            "notes": request.notes,
        }

        # Execute use case
        order = await use_case.execute(order_data)

        logger.info(f"Order created: {order.order_number} for brand {brand_id}")

        return _to_response(order)

    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e),
        )
    except Exception as e:
        import traceback
        logger.error(f"Error creating order: {e}")
        logger.error(f"Order request data: brand_id={brand_id}, customer={request.customer_name}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create order: {str(e)}",
        )


@router.get(
    "/{order_number}",
    response_model=OrderResponse,
    summary="Get order by order number",
    description="Retrieve order details by the human-readable order number.",
)
async def get_order_by_number(
    order_number: Annotated[str, Path(description="Order number (e.g., 20260119-XXXX)")],
    order_repo: Annotated[OrderRepositoryImpl, Depends(get_order_repository)],
):
    """Get order by order number."""
    try:
        use_case = GetOrder(order_repo)
        order = await use_case.execute_by_order_number(order_number)
        return _to_response(order)

    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Error getting order: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get order",
        )


@router.get(
    "/id/{order_id}",
    response_model=OrderResponse,
    summary="Get order by ID",
    description="Retrieve order details by UUID.",
)
async def get_order_by_id(
    order_id: Annotated[UUID, Path(description="Order UUID")],
    order_repo: Annotated[OrderRepositoryImpl, Depends(get_order_repository)],
):
    """Get order by ID."""
    try:
        use_case = GetOrder(order_repo)
        order = await use_case.execute_by_id(order_id)
        return _to_response(order)

    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Error getting order: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get order",
        )


@router.get(
    "/brands/{brand_id}",
    response_model=OrderListResponse,
    summary="List orders for a brand",
    description="Retrieve orders for a specific brand with optional filters.",
)
async def list_orders_by_brand(
    brand_id: Annotated[UUID, Path(description="Brand ID")],
    order_repo: Annotated[OrderRepositoryImpl, Depends(get_order_repository)],
    status_filter: Annotated[
        OrderStatusEnum | None,
        Query(alias="status", description="Filter by status"),
    ] = None,
    skip: Annotated[int, Query(ge=0, description="Skip records")] = 0,
    limit: Annotated[int, Query(ge=1, le=100, description="Limit records")] = 20,
):
    """List orders for a brand."""
    try:
        use_case = GetOrdersByBrand(order_repo)
        orders = await use_case.execute(
            brand_id=brand_id,
            status=status_filter.value if status_filter else None,
            skip=skip,
            limit=limit,
        )

        # Get total count
        total = await order_repo.count_by_brand(
            brand_id=brand_id,
            status=status_filter.value if status_filter else None,
        )

        return OrderListResponse(
            orders=[_to_response(order) for order in orders],
            total=total,
            skip=skip,
            limit=limit,
        )

    except Exception as e:
        logger.error(f"Error listing orders: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list orders",
        )


@router.get(
    "/brands/{brand_id}/active",
    response_model=list[OrderResponse],
    summary="Get active orders for a brand",
    description="Retrieve all non-completed/cancelled orders for a brand.",
)
async def get_active_orders(
    brand_id: Annotated[UUID, Path(description="Brand ID")],
    order_repo: Annotated[OrderRepositoryImpl, Depends(get_order_repository)],
):
    """Get active orders for a brand."""
    try:
        use_case = GetActiveOrders(order_repo)
        orders = await use_case.execute(brand_id)
        return [_to_response(order) for order in orders]

    except Exception as e:
        logger.error(f"Error getting active orders: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get active orders",
        )


@router.patch(
    "/{order_id}/status",
    response_model=OrderResponse,
    summary="Update order status",
    description="Update the status of an order.",
)
async def update_order_status(
    order_id: Annotated[UUID, Path(description="Order UUID")],
    request: UpdateOrderStatusRequest,
    order_repo: Annotated[OrderRepositoryImpl, Depends(get_order_repository)],
):
    """Update order status."""
    try:
        use_case = UpdateOrderStatus(order_repo)
        order = await use_case.execute(order_id, request.status.value)

        logger.info(f"Order {order.order_number} status updated to {request.status.value}")

        return _to_response(order)

    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Error updating order status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update order status",
        )


@router.post(
    "/{order_id}/cancel",
    response_model=OrderResponse,
    summary="Cancel an order",
    description="Cancel an order if it hasn't been completed.",
)
async def cancel_order(
    order_id: Annotated[UUID, Path(description="Order UUID")],
    order_repo: Annotated[OrderRepositoryImpl, Depends(get_order_repository)],
):
    """Cancel an order."""
    try:
        use_case = CancelOrder(order_repo)
        order = await use_case.execute(order_id)

        logger.info(f"Order {order.order_number} cancelled")

        return _to_response(order)

    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Error cancelling order: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to cancel order",
        )
