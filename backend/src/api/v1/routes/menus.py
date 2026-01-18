"""Menu API routes."""
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.v1.schemas.error_schemas import COMMON_RESPONSES
from src.api.v1.schemas.menu_schemas import (
    CategoryCreateRequest,
    CategoryResponse,
    CategoryUpdateRequest,
    MenuResponse,
    MenuUploadRequest,
)
from src.application.use_cases.upload_menu import UploadMenu
from src.domain.entities.category import Category
from src.domain.exceptions import NotFoundError, ValidationError
from src.domain.services.menu_engine import MenuEngine
from src.infrastructure.database.session import get_async_session
from src.infrastructure.repositories.brand_repository_impl import BrandRepositoryImpl
from src.infrastructure.repositories.menu_repository_impl import MenuRepositoryImpl

router = APIRouter(prefix="/brands/{brand_id}/menu", tags=["Menus"])


# Dependency to get repositories
async def get_menu_repository(
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> MenuRepositoryImpl:
    """Get menu repository dependency."""
    return MenuRepositoryImpl(session)


async def get_brand_repository(
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> BrandRepositoryImpl:
    """Get brand repository dependency."""
    return BrandRepositoryImpl(session)


@router.post(
    "",
    response_model=MenuResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {"description": "Menu uploaded successfully"},
        **COMMON_RESPONSES,
    },
    summary="Upload complete menu",
    description="Upload a complete menu for a brand. This will replace any existing menu data.",
)
async def upload_menu(
    brand_id: UUID,
    request: MenuUploadRequest,
    menu_repository: Annotated[MenuRepositoryImpl, Depends(get_menu_repository)],
    brand_repository: Annotated[BrandRepositoryImpl, Depends(get_brand_repository)],
) -> MenuResponse:
    """Upload complete menu for a brand.

    Args:
        brand_id: Brand UUID
        request: Menu upload request with categories
        menu_repository: Menu repository
        brand_repository: Brand repository

    Returns:
        Uploaded menu

    Raises:
        HTTPException: If brand not found or validation fails
    """
    try:
        # Create use case
        menu_engine = MenuEngine()
        use_case = UploadMenu(
            brand_repository=brand_repository,
            menu_repository=menu_repository,
            menu_engine=menu_engine,
        )

        # Execute use case
        menu_data = request.model_dump()
        categories = await use_case.execute(brand_id, menu_data)

        # Convert to response
        return _convert_categories_to_response(categories)

    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@router.get(
    "",
    response_model=MenuResponse,
    responses={
        200: {"description": "Menu retrieved successfully"},
        **COMMON_RESPONSES,
    },
    summary="Get complete menu",
    description="Retrieve the complete menu for a brand.",
)
async def get_menu(
    brand_id: UUID,
    menu_repository: Annotated[MenuRepositoryImpl, Depends(get_menu_repository)],
    brand_repository: Annotated[BrandRepositoryImpl, Depends(get_brand_repository)],
) -> MenuResponse:
    """Get complete menu for a brand.

    Args:
        brand_id: Brand UUID
        menu_repository: Menu repository
        brand_repository: Brand repository

    Returns:
        Complete menu

    Raises:
        HTTPException: If brand not found
    """
    # Verify brand exists
    brand = await brand_repository.get_by_id(brand_id)
    if brand is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Brand not found: {brand_id}",
        )

    # Get full menu
    menu_data = await menu_repository.get_full_menu(brand_id)

    return MenuResponse(**menu_data)


@router.get(
    "/categories",
    response_model=list[CategoryResponse],
    responses={
        200: {"description": "Categories retrieved successfully"},
        **COMMON_RESPONSES,
    },
    summary="List all categories",
    description="Retrieve all categories for a brand.",
)
async def list_categories(
    brand_id: UUID,
    menu_repository: Annotated[MenuRepositoryImpl, Depends(get_menu_repository)],
    brand_repository: Annotated[BrandRepositoryImpl, Depends(get_brand_repository)],
    include_items: bool = True,
) -> list[CategoryResponse]:
    """List all categories for a brand.

    Args:
        brand_id: Brand UUID
        menu_repository: Menu repository
        brand_repository: Brand repository
        include_items: Whether to include menu items

    Returns:
        List of categories

    Raises:
        HTTPException: If brand not found
    """
    # Verify brand exists
    brand = await brand_repository.get_by_id(brand_id)
    if brand is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Brand not found: {brand_id}",
        )

    # Get categories
    categories = await menu_repository.get_categories_by_brand(
        brand_id, include_items=include_items
    )

    # Convert to response
    return [_convert_category_to_response(cat) for cat in categories]


@router.post(
    "/categories",
    response_model=CategoryResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {"description": "Category created successfully"},
        **COMMON_RESPONSES,
    },
    summary="Create a category",
    description="Create a new category for a brand.",
)
async def create_category(
    brand_id: UUID,
    request: CategoryCreateRequest,
    menu_repository: Annotated[MenuRepositoryImpl, Depends(get_menu_repository)],
    brand_repository: Annotated[BrandRepositoryImpl, Depends(get_brand_repository)],
) -> CategoryResponse:
    """Create a new category.

    Args:
        brand_id: Brand UUID
        request: Category creation request
        menu_repository: Menu repository
        brand_repository: Brand repository

    Returns:
        Created category

    Raises:
        HTTPException: If brand not found or validation fails
    """
    try:
        # Verify brand exists
        brand = await brand_repository.get_by_id(brand_id)
        if brand is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Brand not found: {brand_id}",
            )

        # Create category entity
        category = Category(
            name=request.name,
            description=request.description,
            display_order=request.display_order,
        )

        # Create in database
        created_category = await menu_repository.create_category(brand_id, category)

        # Convert to response
        return _convert_category_to_response(created_category)

    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@router.get(
    "/categories/{category_id}",
    response_model=CategoryResponse,
    responses={
        200: {"description": "Category retrieved successfully"},
        **COMMON_RESPONSES,
    },
    summary="Get category by ID",
    description="Retrieve a specific category by its ID.",
)
async def get_category(
    brand_id: UUID,
    category_id: UUID,
    menu_repository: Annotated[MenuRepositoryImpl, Depends(get_menu_repository)],
) -> CategoryResponse:
    """Get category by ID.

    Args:
        brand_id: Brand UUID (for validation)
        category_id: Category UUID
        menu_repository: Menu repository

    Returns:
        Category information

    Raises:
        HTTPException: If category not found
    """
    category = await menu_repository.get_category_by_id(category_id)

    if category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category not found: {category_id}",
        )

    # Convert to response
    return _convert_category_to_response(category)


@router.patch(
    "/categories/{category_id}",
    response_model=CategoryResponse,
    responses={
        200: {"description": "Category updated successfully"},
        **COMMON_RESPONSES,
    },
    summary="Update a category",
    description="Update an existing category.",
)
async def update_category(
    brand_id: UUID,
    category_id: UUID,
    request: CategoryUpdateRequest,
    menu_repository: Annotated[MenuRepositoryImpl, Depends(get_menu_repository)],
) -> CategoryResponse:
    """Update a category.

    Args:
        brand_id: Brand UUID (for validation)
        category_id: Category UUID
        request: Category update request
        menu_repository: Menu repository

    Returns:
        Updated category

    Raises:
        HTTPException: If category not found or validation fails
    """
    try:
        # Get existing category
        category = await menu_repository.get_category_by_id(category_id)
        if category is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Category not found: {category_id}",
            )

        # Update fields
        update_data = request.model_dump(exclude_none=True)
        if "name" in update_data:
            category.name = update_data["name"]
        if "description" in update_data:
            category.description = update_data["description"]
        if "display_order" in update_data:
            category.display_order = update_data["display_order"]

        # Update in database
        updated_category = await menu_repository.update_category(category)

        # Convert to response
        return _convert_category_to_response(updated_category)

    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e


@router.delete(
    "/categories/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        204: {"description": "Category deleted successfully"},
        **COMMON_RESPONSES,
    },
    summary="Delete a category",
    description="Delete a category by ID. This will also delete all associated menu items.",
)
async def delete_category(
    brand_id: UUID,
    category_id: UUID,
    menu_repository: Annotated[MenuRepositoryImpl, Depends(get_menu_repository)],
) -> None:
    """Delete a category.

    Args:
        brand_id: Brand UUID (for validation)
        category_id: Category UUID
        menu_repository: Menu repository

    Raises:
        HTTPException: If category not found
    """
    deleted = await menu_repository.delete_category(category_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category not found: {category_id}",
        )


# Helper functions
def _convert_category_to_response(category: Category) -> CategoryResponse:
    """Convert Category entity to CategoryResponse schema."""
    from src.api.v1.schemas.menu_schemas import (
        CustomizationOptionResponse,
        MenuItemResponse,
    )

    menu_items = [
        MenuItemResponse(
            id=item.id,
            name=item.name,
            description=item.description,
            price=item.price,
            display_order=item.display_order,
            customization_options=[
                CustomizationOptionResponse(
                    id=opt.id,
                    option_type=opt.option_type,
                    name=opt.name,
                    price_adjustment=opt.price_adjustment,
                )
                for opt in item.customization_options
            ],
        )
        for item in category.menu_items
    ]

    return CategoryResponse(
        id=category.id,
        name=category.name,
        description=category.description,
        display_order=category.display_order,
        menu_items=menu_items,
    )


def _convert_categories_to_response(categories: list[Category]) -> MenuResponse:
    """Convert list of Category entities to MenuResponse schema."""
    return MenuResponse(
        categories=[_convert_category_to_response(cat) for cat in categories]
    )
