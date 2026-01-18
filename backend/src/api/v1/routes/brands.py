"""Brand API routes."""
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.v1.schemas.brand_schemas import (
    BrandCreateRequest,
    BrandResponse,
    BrandUpdateRequest,
)
from src.api.v1.schemas.error_schemas import COMMON_RESPONSES
from src.application.use_cases.create_brand import CreateBrand
from src.application.use_cases.get_brand_by_slug import GetBrandBySlug
from src.domain.entities.brand import Brand
from src.domain.exceptions import DuplicateSlugError, NotFoundError, ValidationError
from src.domain.services.menu_engine import MenuEngine
from src.domain.services.theme_engine import ThemeEngine
from src.infrastructure.database.session import get_async_session
from src.infrastructure.repositories.brand_repository_impl import BrandRepositoryImpl

router = APIRouter(prefix="/brands", tags=["Brands"])


# Helper functions for theme_config naming conversion
def to_camel_case(theme_config: dict) -> dict:
    """Convert theme_config from snake_case to camelCase for domain layer."""
    mapping = {
        "primary_color": "primaryColor",
        "secondary_color": "secondaryColor",
        "accent_color": "accentColor",
        "background_color": "backgroundColor",
        "text_color": "textColor",
        "font_family": "fontFamily",
    }
    return {mapping.get(k, k): v for k, v in theme_config.items() if v is not None}


def to_snake_case(theme_config: dict) -> dict:
    """Convert theme_config from camelCase to snake_case for API response."""
    mapping = {
        "primaryColor": "primary_color",
        "secondaryColor": "secondary_color",
        "accentColor": "accent_color",
        "backgroundColor": "background_color",
        "textColor": "text_color",
        "fontFamily": "font_family",
    }
    return {mapping.get(k, k): v for k, v in theme_config.items() if v is not None}


# Dependency to get brand repository
async def get_brand_repository(
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> BrandRepositoryImpl:
    """Get brand repository dependency."""
    return BrandRepositoryImpl(session)


@router.post(
    "",
    response_model=BrandResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {"description": "Brand created successfully"},
        **COMMON_RESPONSES,
    },
    summary="Create a new brand",
    description="Create a new brand with theme configuration. Slug is auto-generated from name if not provided.",
)
async def create_brand(
    request: BrandCreateRequest,
    repository: Annotated[BrandRepositoryImpl, Depends(get_brand_repository)],
) -> BrandResponse:
    """Create a new brand.

    Args:
        request: Brand creation request
        repository: Brand repository

    Returns:
        Created brand

    Raises:
        HTTPException: If validation fails or slug already exists
    """
    try:
        # Create use case with dependencies
        menu_engine = MenuEngine()
        theme_engine = ThemeEngine()
        use_case = CreateBrand(
            brand_repository=repository,
            menu_engine=menu_engine,
            theme_engine=theme_engine,
        )

        # Prepare brand data and convert theme_config to camelCase
        brand_data = request.model_dump(exclude_none=True)
        if "theme_config" in brand_data:
            brand_data["theme_config"] = to_camel_case(brand_data["theme_config"])

        # Execute use case
        brand = await use_case.execute(brand_data)

        # Convert to response (convert theme_config back to snake_case)
        return BrandResponse(
            id=brand.id,
            name=brand.name,
            slug=brand.slug,
            description=brand.description,
            logo_url=brand.logo_url,
            theme_config=to_snake_case(brand.theme_config.to_dict()),
            is_active=brand.is_active,
        )

    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e
    except DuplicateSlugError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        ) from e


@router.get(
    "/slug/{slug}",
    response_model=BrandResponse,
    responses={
        200: {"description": "Brand found"},
        **COMMON_RESPONSES,
    },
    summary="Get brand by slug",
    description="Retrieve a brand by its URL-friendly slug.",
)
async def get_brand_by_slug(
    slug: str,
    repository: Annotated[BrandRepositoryImpl, Depends(get_brand_repository)],
) -> BrandResponse:
    """Get brand by slug.

    Args:
        slug: Brand slug
        repository: Brand repository

    Returns:
        Brand information

    Raises:
        HTTPException: If brand not found
    """
    try:
        # Create use case
        use_case = GetBrandBySlug(brand_repository=repository)

        # Execute use case
        brand = await use_case.execute(slug)

        # Check if brand was found
        if brand is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Brand not found: {slug}",
            )

        # Convert to response (convert theme_config to snake_case)
        return BrandResponse(
            id=brand.id,
            name=brand.name,
            slug=brand.slug,
            description=brand.description,
            logo_url=brand.logo_url,
            theme_config=to_snake_case(brand.theme_config.to_dict()),
            is_active=brand.is_active,
        )

    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e


@router.get(
    "/{brand_id}",
    response_model=BrandResponse,
    responses={
        200: {"description": "Brand found"},
        **COMMON_RESPONSES,
    },
    summary="Get brand by ID",
    description="Retrieve a brand by its UUID.",
)
async def get_brand_by_id(
    brand_id: UUID,
    repository: Annotated[BrandRepositoryImpl, Depends(get_brand_repository)],
) -> BrandResponse:
    """Get brand by ID.

    Args:
        brand_id: Brand UUID
        repository: Brand repository

    Returns:
        Brand information

    Raises:
        HTTPException: If brand not found
    """
    brand = await repository.get_by_id(brand_id)

    if brand is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Brand not found: {brand_id}",
        )

    # Convert to response (convert theme_config to snake_case)
    return BrandResponse(
        id=brand.id,
        name=brand.name,
        slug=brand.slug,
        description=brand.description,
        logo_url=brand.logo_url,
        theme_config=to_snake_case(brand.theme_config.to_dict()),
        is_active=brand.is_active,
    )


@router.get(
    "",
    response_model=list[BrandResponse],
    responses={
        200: {"description": "List of brands"},
        **COMMON_RESPONSES,
    },
    summary="List all brands",
    description="Retrieve a list of all brands with pagination.",
)
async def list_brands(
    repository: Annotated[BrandRepositoryImpl, Depends(get_brand_repository)],
    skip: int = 0,
    limit: int = 100,
    active_only: bool = False,
) -> list[BrandResponse]:
    """List all brands.

    Args:
        repository: Brand repository
        skip: Number of records to skip
        limit: Maximum number of records to return
        active_only: If True, only return active brands

    Returns:
        List of brands
    """
    if active_only:
        brands = await repository.get_active_brands(skip=skip, limit=limit)
    else:
        brands = await repository.get_all(skip=skip, limit=limit)

    # Convert to response (convert theme_config to snake_case)
    return [
        BrandResponse(
            id=brand.id,
            name=brand.name,
            slug=brand.slug,
            description=brand.description,
            logo_url=brand.logo_url,
            theme_config=to_snake_case(brand.theme_config.to_dict()),
            is_active=brand.is_active,
        )
        for brand in brands
    ]


@router.patch(
    "/{brand_id}",
    response_model=BrandResponse,
    responses={
        200: {"description": "Brand updated successfully"},
        **COMMON_RESPONSES,
    },
    summary="Update a brand",
    description="Update an existing brand's information.",
)
async def update_brand(
    brand_id: UUID,
    request: BrandUpdateRequest,
    repository: Annotated[BrandRepositoryImpl, Depends(get_brand_repository)],
) -> BrandResponse:
    """Update a brand.

    Args:
        brand_id: Brand UUID
        request: Brand update request
        repository: Brand repository

    Returns:
        Updated brand

    Raises:
        HTTPException: If brand not found or validation fails
    """
    try:
        # Get existing brand
        brand = await repository.get_by_id(brand_id)
        if brand is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Brand not found: {brand_id}",
            )

        # Update fields
        update_data = request.model_dump(exclude_none=True)
        if "name" in update_data:
            brand.name = update_data["name"]
        if "slug" in update_data:
            brand.slug = update_data["slug"]
        if "description" in update_data:
            brand.description = update_data["description"]
        if "logo_url" in update_data:
            brand.logo_url = update_data["logo_url"]
        if "theme_config" in update_data:
            # Convert theme_config to camelCase and use update_theme method
            brand.update_theme(to_camel_case(update_data["theme_config"]))
        if "is_active" in update_data:
            if update_data["is_active"]:
                brand.activate()
            else:
                brand.deactivate()

        # Update in database
        updated_brand = await repository.update(brand)

        # Convert to response (convert theme_config to snake_case)
        return BrandResponse(
            id=updated_brand.id,
            name=updated_brand.name,
            slug=updated_brand.slug,
            description=updated_brand.description,
            logo_url=updated_brand.logo_url,
            theme_config=to_snake_case(updated_brand.theme_config.to_dict()),
            is_active=updated_brand.is_active,
        )

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
    "/{brand_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        204: {"description": "Brand deleted successfully"},
        **COMMON_RESPONSES,
    },
    summary="Delete a brand",
    description="Delete a brand by ID. This will also delete all associated menu data.",
)
async def delete_brand(
    brand_id: UUID,
    repository: Annotated[BrandRepositoryImpl, Depends(get_brand_repository)],
) -> None:
    """Delete a brand.

    Args:
        brand_id: Brand UUID
        repository: Brand repository

    Raises:
        HTTPException: If brand not found
    """
    deleted = await repository.delete(brand_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Brand not found: {brand_id}",
        )
