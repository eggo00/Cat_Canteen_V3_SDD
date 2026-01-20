"""Authentication API schemas."""
import re
from uuid import UUID

from pydantic import Field, field_validator

from . import BaseSchema, IDSchema

# Email validation regex
EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")


def _validate_email(v: str) -> str:
    """Validate email format helper."""
    v = v.strip().lower()
    if not EMAIL_REGEX.match(v):
        raise ValueError("Invalid email format")
    return v


class LoginRequest(BaseSchema):
    """Request schema for user login."""

    email: str = Field(
        ...,
        description="User email address",
        examples=["user@example.com"],
        max_length=255,
    )
    password: str = Field(
        ...,
        description="User password",
        min_length=1,
    )

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        """Validate email format."""
        return _validate_email(v)


class TokenResponse(BaseSchema):
    """Response schema for authentication tokens."""

    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field("bearer", description="Token type")


class RefreshTokenRequest(BaseSchema):
    """Request schema for token refresh."""

    refresh_token: str = Field(
        ...,
        description="JWT refresh token",
    )


class UserResponse(IDSchema):
    """Response schema for user data."""

    email: str = Field(..., description="User email address")
    name: str | None = Field(None, description="User display name")
    role: str = Field(..., description="User role (customer, staff, admin, super_admin)")
    brand_id: UUID | None = Field(None, description="Associated brand ID")
    is_active: bool = Field(..., description="User account active status")


class UserCreateRequest(BaseSchema):
    """Request schema for creating a user."""

    email: str = Field(
        ...,
        description="User email address",
        examples=["newuser@example.com"],
        max_length=255,
    )
    password: str = Field(
        ...,
        description="User password",
        min_length=8,
        max_length=128,
    )
    name: str | None = Field(
        None,
        description="User display name",
        max_length=255,
    )
    role: str = Field(
        "customer",
        description="User role (customer, staff, admin, super_admin)",
        examples=["customer", "staff", "admin"],
    )
    brand_id: UUID | None = Field(
        None,
        description="Associated brand ID (required for non-super_admin)",
    )

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        """Validate email format."""
        return _validate_email(v)

    @field_validator("role")
    @classmethod
    def validate_role(cls, v: str) -> str:
        """Validate role is valid."""
        valid_roles = {"customer", "staff", "admin", "super_admin"}
        v = v.lower()
        if v not in valid_roles:
            raise ValueError(f"Invalid role. Must be one of: {', '.join(valid_roles)}")
        return v


class UserUpdateRequest(BaseSchema):
    """Request schema for updating a user."""

    email: str | None = Field(
        None,
        description="User email address",
        max_length=255,
    )
    name: str | None = Field(
        None,
        description="User display name",
        max_length=255,
    )
    role: str | None = Field(
        None,
        description="User role",
    )
    brand_id: UUID | None = Field(
        None,
        description="Associated brand ID",
    )
    is_active: bool | None = Field(
        None,
        description="User account active status",
    )

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str | None) -> str | None:
        """Validate email format."""
        if v is None:
            return v
        return _validate_email(v)

    @field_validator("role")
    @classmethod
    def validate_role(cls, v: str | None) -> str | None:
        """Validate role is valid."""
        if v is None:
            return v
        valid_roles = {"customer", "staff", "admin", "super_admin"}
        v = v.lower()
        if v not in valid_roles:
            raise ValueError(f"Invalid role. Must be one of: {', '.join(valid_roles)}")
        return v


class PasswordChangeRequest(BaseSchema):
    """Request schema for changing password."""

    current_password: str = Field(
        ...,
        description="Current password",
        min_length=1,
    )
    new_password: str = Field(
        ...,
        description="New password",
        min_length=8,
        max_length=128,
    )


class LoginResponse(BaseSchema):
    """Response schema for successful login."""

    user: UserResponse = Field(..., description="User data")
    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field("bearer", description="Token type")


__all__ = [
    "LoginRequest",
    "TokenResponse",
    "RefreshTokenRequest",
    "UserResponse",
    "UserCreateRequest",
    "UserUpdateRequest",
    "PasswordChangeRequest",
    "LoginResponse",
]
