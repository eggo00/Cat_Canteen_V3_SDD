"""Authentication API routes."""
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.v1.dependencies import AdminUser, CurrentUser
from src.api.v1.schemas.auth_schemas import (
    LoginRequest,
    LoginResponse,
    PasswordChangeRequest,
    RefreshTokenRequest,
    TokenResponse,
    UserCreateRequest,
    UserResponse,
)
from src.application.use_cases.auth.login import Login
from src.application.use_cases.auth.refresh_token import RefreshToken
from src.application.use_cases.auth.register_user import RegisterUser
from src.domain.entities.user import User, UserRole
from src.domain.exceptions import (
    DuplicateEmailError,
    InvalidCredentialsError,
    InvalidTokenError,
    NotFoundError,
    TokenExpiredError,
    UnauthorizedError,
    ValidationError,
)
from src.infrastructure.auth.jwt_handler import JWTHandler
from src.infrastructure.auth.password_hasher import PasswordHasher
from src.infrastructure.database.session import get_async_session
from src.infrastructure.logging import get_security_logger
from src.infrastructure.repositories.brand_repository_impl import BrandRepositoryImpl
from src.infrastructure.repositories.user_repository_impl import UserRepositoryImpl

router = APIRouter(prefix="/auth", tags=["Authentication"])

# Security logger for auth events
security_logger = get_security_logger()


# Helper to convert User entity to UserResponse
def _user_to_response(user: User) -> UserResponse:
    """Convert User entity to UserResponse schema."""
    return UserResponse(
        id=user.id,
        email=user.email,
        name=user.name,
        role=user.role.value,
        brand_id=user.brand_id,
        is_active=user.is_active,
    )


def _get_client_ip(request: Request) -> str | None:
    """Extract client IP from request."""
    # Check for forwarded headers (behind proxy)
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    if request.client:
        return request.client.host
    return None


@router.post(
    "/login",
    response_model=LoginResponse,
    summary="User login",
    description="Authenticate user with email and password",
)
async def login(
    request: LoginRequest,
    http_request: Request,
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> LoginResponse:
    """Authenticate user and return tokens.

    Args:
        request: Login request with email and password
        http_request: HTTP request for client IP extraction
        session: Database session

    Returns:
        LoginResponse: User data and authentication tokens

    Raises:
        HTTPException: If credentials are invalid
    """
    client_ip = _get_client_ip(http_request)
    user_repository = UserRepositoryImpl(session)
    login_use_case = Login(
        user_repository=user_repository,
        password_hasher=PasswordHasher,
        jwt_handler=JWTHandler,
    )

    try:
        result = await login_use_case.execute(
            email=request.email,
            password=request.password,
        )
    except InvalidCredentialsError as e:
        # Log failed login attempt
        security_logger.log_login_failure(
            email=request.email,
            ip_address=client_ip,
            reason=str(e),
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        ) from e
    except ValidationError as e:
        # Log validation failure as login failure
        security_logger.log_login_failure(
            email=request.email,
            ip_address=client_ip,
            reason=f"Validation error: {e}",
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e

    # Log successful login
    security_logger.log_login_success(
        email=result.user.email,
        user_id=str(result.user.id),
        ip_address=client_ip,
    )

    return LoginResponse(
        user=_user_to_response(result.user),
        access_token=result.access_token,
        refresh_token=result.refresh_token,
        token_type=result.token_type,
    )


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Refresh tokens",
    description="Get new access and refresh tokens using a valid refresh token",
)
async def refresh_token(
    request: RefreshTokenRequest,
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> TokenResponse:
    """Refresh authentication tokens.

    Args:
        request: Refresh token request
        session: Database session

    Returns:
        TokenResponse: New authentication tokens

    Raises:
        HTTPException: If refresh token is invalid or expired
    """
    user_repository = UserRepositoryImpl(session)
    refresh_use_case = RefreshToken(
        user_repository=user_repository,
        jwt_handler=JWTHandler,
    )

    try:
        result = await refresh_use_case.execute(
            refresh_token=request.refresh_token,
        )
    except TokenExpiredError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except UnauthorizedError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )

    return TokenResponse(
        access_token=result.access_token,
        refresh_token=result.refresh_token,
        token_type=result.token_type,
    )


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user",
    description="Get the currently authenticated user's information",
)
async def get_current_user_info(
    current_user: CurrentUser,
) -> UserResponse:
    """Get current user information.

    Args:
        current_user: Current authenticated user

    Returns:
        UserResponse: Current user data
    """
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        name=current_user.full_name if current_user.full_name else None,
        role=current_user.role,
        brand_id=current_user.brand_id,
        is_active=current_user.is_active,
    )


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register new user",
    description="Register a new user (admin only, or super_admin for admin users)",
)
async def register_user(
    request: UserCreateRequest,
    session: Annotated[AsyncSession, Depends(get_async_session)],
    current_user: AdminUser,
) -> UserResponse:
    """Register a new user.

    Permissions:
    - admin: Can create staff/customer in their own brand
    - super_admin: Can create any user in any brand

    Args:
        request: User creation request
        session: Database session
        current_user: Current authenticated admin user

    Returns:
        UserResponse: Created user data

    Raises:
        HTTPException: If validation fails or user lacks permission
    """
    user_repository = UserRepositoryImpl(session)
    brand_repository = BrandRepositoryImpl(session)
    register_use_case = RegisterUser(
        user_repository=user_repository,
        brand_repository=brand_repository,
        password_hasher=PasswordHasher,
    )

    # Convert current UserModel to User entity for permission check
    current_user_entity = User(
        id=current_user.id,
        email=current_user.email,
        password_hash=current_user.password_hash,
        role=UserRole(current_user.role),
        brand_id=current_user.brand_id,
        name=current_user.full_name,
        is_active=current_user.is_active,
    )

    try:
        result = await register_use_case.execute(
            email=request.email,
            password=request.password,
            role=request.role,
            brand_id=request.brand_id,
            name=request.name,
            current_user=current_user_entity,
        )
    except DuplicateEmailError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        ) from e
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e
    except UnauthorizedError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        ) from e
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e

    return _user_to_response(result.user)


@router.put(
    "/password",
    response_model=UserResponse,
    summary="Change password",
    description="Change the current user's password",
)
async def change_password(
    request: PasswordChangeRequest,
    session: Annotated[AsyncSession, Depends(get_async_session)],
    current_user: CurrentUser,
) -> UserResponse:
    """Change current user's password.

    Args:
        request: Password change request
        session: Database session
        current_user: Current authenticated user

    Returns:
        UserResponse: Updated user data

    Raises:
        HTTPException: If current password is incorrect
    """
    # Verify current password
    if not PasswordHasher.verify_password(request.current_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Current password is incorrect",
        )

    # Hash new password and update
    new_hash = PasswordHasher.hash_password(request.new_password)
    current_user.password_hash = new_hash

    await session.flush()
    await session.refresh(current_user)

    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        name=current_user.full_name if current_user.full_name else None,
        role=current_user.role,
        brand_id=current_user.brand_id,
        is_active=current_user.is_active,
    )


@router.get(
    "/users",
    response_model=list[UserResponse],
    summary="List users",
    description="List all users (super_admin) or users in current brand (admin)",
)
async def list_users(
    session: Annotated[AsyncSession, Depends(get_async_session)],
    current_user: AdminUser,
    role: str | None = None,
    brand_id: UUID | None = None,
    skip: int = 0,
    limit: int = 100,
) -> list[UserResponse]:
    """List users.

    - super_admin: Can list all users or filter by brand
    - admin: Can only list users in their own brand

    Args:
        session: Database session
        current_user: Current authenticated admin user
        role: Optional role filter
        brand_id: Optional brand ID filter (super_admin only)
        skip: Number of records to skip
        limit: Maximum number of records

    Returns:
        list[UserResponse]: List of users
    """
    user_repository = UserRepositoryImpl(session)

    # Convert role string to UserRole if provided
    role_filter = None
    if role:
        try:
            role_filter = UserRole(role.lower())
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid role: {role}",
            )

    # Determine which users to fetch based on current user's role
    if current_user.role == "super_admin":
        # Super admin can list any brand's users or all users
        if brand_id:
            users = await user_repository.get_by_brand(
                brand_id=brand_id,
                skip=skip,
                limit=limit,
                role=role_filter,
            )
        else:
            users = await user_repository.get_all(
                skip=skip,
                limit=limit,
                role=role_filter,
            )
    else:
        # Admin can only list users in their own brand
        if brand_id and brand_id != current_user.brand_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot list users from other brands",
            )
        users = await user_repository.get_by_brand(
            brand_id=current_user.brand_id,
            skip=skip,
            limit=limit,
            role=role_filter,
        )

    return [_user_to_response(user) for user in users]


@router.get(
    "/users/{user_id}",
    response_model=UserResponse,
    summary="Get user by ID",
    description="Get user details by ID (admin only)",
)
async def get_user(
    user_id: UUID,
    session: Annotated[AsyncSession, Depends(get_async_session)],
    current_user: AdminUser,
) -> UserResponse:
    """Get user by ID.

    Args:
        user_id: User ID to fetch
        session: Database session
        current_user: Current authenticated admin user

    Returns:
        UserResponse: User data

    Raises:
        HTTPException: If user not found or access denied
    """
    user_repository = UserRepositoryImpl(session)
    user = await user_repository.get_by_id(user_id)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User not found: {user_id}",
        )

    # Check brand access (non-super_admin can only view users in their brand)
    if current_user.role != "super_admin" and user.brand_id != current_user.brand_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot view users from other brands",
        )

    return _user_to_response(user)


@router.delete(
    "/users/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete user",
    description="Delete a user (admin only)",
)
async def delete_user(
    user_id: UUID,
    session: Annotated[AsyncSession, Depends(get_async_session)],
    current_user: AdminUser,
) -> None:
    """Delete a user.

    Args:
        user_id: User ID to delete
        session: Database session
        current_user: Current authenticated admin user

    Raises:
        HTTPException: If user not found or access denied
    """
    user_repository = UserRepositoryImpl(session)
    user = await user_repository.get_by_id(user_id)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User not found: {user_id}",
        )

    # Prevent self-deletion
    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account",
        )

    # Check permissions
    if current_user.role != "super_admin":
        # Admin can only delete users in their brand
        if user.brand_id != current_user.brand_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot delete users from other brands",
            )
        # Admin cannot delete other admins
        if user.role == UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin cannot delete other admin users",
            )

    await user_repository.delete(user_id)
