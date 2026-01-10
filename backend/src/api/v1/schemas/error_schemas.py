"""Error response schemas for API."""
from typing import Any

from pydantic import Field

from . import BaseSchema


class ErrorDetail(BaseSchema):
    """Detailed error information."""

    field: str | None = Field(None, description="Field name that caused the error")
    message: str = Field(..., description="Error message")
    code: str | None = Field(None, description="Error code for client-side handling")


class ErrorResponse(BaseSchema):
    """Standard error response format."""

    detail: str = Field(..., description="Error message")
    errors: list[ErrorDetail] | None = Field(
        None, description="List of detailed errors (e.g., validation errors)"
    )
    error_code: str | None = Field(
        None, description="Machine-readable error code"
    )


class ValidationErrorResponse(BaseSchema):
    """Validation error response (422 Unprocessable Entity)."""

    detail: list[dict[str, Any]] = Field(
        ...,
        description="List of validation errors from Pydantic",
        examples=[
            [
                {
                    "loc": ["body", "email"],
                    "msg": "value is not a valid email address",
                    "type": "value_error.email",
                }
            ]
        ],
    )


class UnauthorizedResponse(BaseSchema):
    """Unauthorized error response (401)."""

    detail: str = Field(
        "Not authenticated",
        description="Error message",
    )


class ForbiddenResponse(BaseSchema):
    """Forbidden error response (403)."""

    detail: str = Field(
        "Access forbidden",
        description="Error message",
    )


class NotFoundResponse(BaseSchema):
    """Not found error response (404)."""

    detail: str = Field(
        "Resource not found",
        description="Error message",
    )


class ConflictResponse(BaseSchema):
    """Conflict error response (409)."""

    detail: str = Field(
        "Resource conflict",
        description="Error message",
    )
    conflict_field: str | None = Field(
        None,
        description="Field that caused the conflict (e.g., 'email' for duplicate email)",
    )


class RateLimitResponse(BaseSchema):
    """Rate limit error response (429)."""

    detail: str = Field(
        "Rate limit exceeded",
        description="Error message",
    )
    retry_after: int | None = Field(
        None,
        description="Seconds to wait before retrying",
    )


class InternalServerErrorResponse(BaseSchema):
    """Internal server error response (500)."""

    detail: str = Field(
        "Internal server error",
        description="Error message",
    )
    error: str | None = Field(
        None,
        description="Detailed error information (only in debug mode)",
    )


# Common error responses for OpenAPI documentation
COMMON_RESPONSES = {
    400: {"model": ErrorResponse, "description": "Bad Request"},
    401: {"model": UnauthorizedResponse, "description": "Unauthorized"},
    403: {"model": ForbiddenResponse, "description": "Forbidden"},
    404: {"model": NotFoundResponse, "description": "Not Found"},
    409: {"model": ConflictResponse, "description": "Conflict"},
    422: {"model": ValidationErrorResponse, "description": "Validation Error"},
    429: {"model": RateLimitResponse, "description": "Too Many Requests"},
    500: {"model": InternalServerErrorResponse, "description": "Internal Server Error"},
}


__all__ = [
    "ErrorDetail",
    "ErrorResponse",
    "ValidationErrorResponse",
    "UnauthorizedResponse",
    "ForbiddenResponse",
    "NotFoundResponse",
    "ConflictResponse",
    "RateLimitResponse",
    "InternalServerErrorResponse",
    "COMMON_RESPONSES",
]
