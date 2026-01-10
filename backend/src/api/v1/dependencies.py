"""FastAPI dependencies for authentication and authorization."""
from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.auth.jwt_handler import JWTHandler
from src.infrastructure.database.models import UserModel
from src.infrastructure.database.session import get_async_session

# Security scheme for JWT Bearer tokens
security = HTTPBearer()


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> UserModel:
    """Dependency to get the current authenticated user.

    Args:
        credentials: JWT token from Authorization header
        session: Database session

    Returns:
        UserModel: Current authenticated user

    Raises:
        HTTPException: If token is invalid or user not found
    """
    token = credentials.credentials

    try:
        payload = JWTHandler.decode_token(token)
        user_id = UUID(payload["sub"])
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e

    # Fetch user from database
    from sqlalchemy import select

    result = await session.execute(select(UserModel).where(UserModel.id == user_id))
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )

    return user


async def get_current_active_user(
    current_user: Annotated[UserModel, Depends(get_current_user)],
) -> UserModel:
    """Dependency to get current active user (alias for get_current_user).

    Args:
        current_user: Current user from get_current_user dependency

    Returns:
        UserModel: Current active user
    """
    return current_user


def require_role(*allowed_roles: str):
    """Dependency factory to require specific roles.

    Usage:
        @app.get("/admin")
        async def admin_route(user: Annotated[UserModel, Depends(require_role("admin", "super_admin"))]):
            ...

    Args:
        *allowed_roles: Roles that are allowed to access the endpoint

    Returns:
        Dependency function that checks user role
    """

    async def check_role(
        current_user: Annotated[UserModel, Depends(get_current_user)],
    ) -> UserModel:
        """Check if current user has required role.

        Args:
            current_user: Current authenticated user

        Returns:
            UserModel: Current user if role is allowed

        Raises:
            HTTPException: If user doesn't have required role
        """
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required roles: {', '.join(allowed_roles)}",
            )
        return current_user

    return check_role


def require_brand_access(brand_id: UUID):
    """Dependency factory to ensure user has access to a specific brand.

    Super admins have access to all brands.
    Other users must belong to the requested brand.

    Args:
        brand_id: Brand ID to check access for

    Returns:
        Dependency function that checks brand access
    """

    async def check_brand_access(
        current_user: Annotated[UserModel, Depends(get_current_user)],
    ) -> UserModel:
        """Check if user has access to the brand.

        Args:
            current_user: Current authenticated user

        Returns:
            UserModel: Current user if access is allowed

        Raises:
            HTTPException: If user doesn't have access to the brand
        """
        # Super admins can access all brands
        if current_user.role == "super_admin":
            return current_user

        # Other users must belong to the brand
        if current_user.brand_id != brand_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied. You don't have permission to access this brand.",
            )

        return current_user

    return check_brand_access


# Type aliases for common dependencies
CurrentUser = Annotated[UserModel, Depends(get_current_user)]
CurrentActiveUser = Annotated[UserModel, Depends(get_current_active_user)]
AdminUser = Annotated[UserModel, Depends(require_role("admin", "super_admin"))]
SuperAdminUser = Annotated[UserModel, Depends(require_role("super_admin"))]
