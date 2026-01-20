"""Middleware for FastAPI application."""
import time
from collections.abc import Callable

from fastapi import Request, Response, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from src.infrastructure.config import settings


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """Middleware to handle uncaught exceptions globally."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and handle any exceptions.

        Args:
            request: Incoming HTTP request
            call_next: Next middleware or route handler

        Returns:
            Response: HTTP response
        """
        try:
            response = await call_next(request)
            return response
        except Exception as e:
            # Log the error (in production, use proper logging)
            print(f"Unhandled error: {e}")

            # Return error response
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "detail": "Internal server error",
                    "error": str(e) if settings.DEBUG else "An error occurred",
                },
            )


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log incoming requests and response times."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Log request details and timing.

        Args:
            request: Incoming HTTP request
            call_next: Next middleware or route handler

        Returns:
            Response: HTTP response with timing header
        """
        start_time = time.time()

        # Process request
        response = await call_next(request)

        # Calculate processing time
        process_time = time.time() - start_time

        # Add timing header
        response.headers["X-Process-Time"] = str(process_time)

        # Log request (in production, use proper logging)
        if settings.DEBUG:
            print(
                f"{request.method} {request.url.path} - "
                f"Status: {response.status_code} - "
                f"Time: {process_time:.3f}s"
            )

        return response


class CORSSecurityMiddleware(BaseHTTPMiddleware):
    """Additional CORS security checks (used with CORSMiddleware)."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Add additional security headers.

        Args:
            request: Incoming HTTP request
            call_next: Next middleware or route handler

        Returns:
            Response: HTTP response with security headers
        """
        response = await call_next(request)

        # Add security headers (always applied)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"

        # Production-only headers
        if settings.is_production:
            # HSTS - Force HTTPS
            response.headers["Strict-Transport-Security"] = (
                "max-age=31536000; includeSubDomains; preload"
            )

            # Content Security Policy
            response.headers["Content-Security-Policy"] = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline'; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data: https:; "
                "font-src 'self' https://fonts.gstatic.com; "
                "connect-src 'self' https:; "
                "frame-ancestors 'none'; "
                "base-uri 'self'; "
                "form-action 'self'"
            )

            # Referrer Policy
            response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

            # Permissions Policy
            response.headers["Permissions-Policy"] = (
                "geolocation=(), microphone=(), camera=()"
            )

        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Simple in-memory rate limiting middleware.

    Note: In production, use Redis-based rate limiting for distributed systems.
    """

    def __init__(self, app, calls: int = 100, period: int = 60):
        """Initialize rate limiter.

        Args:
            app: FastAPI application
            calls: Number of calls allowed
            period: Time period in seconds
        """
        super().__init__(app)
        self.calls = calls
        self.period = period
        self.clients: dict[str, list[float]] = {}

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Check rate limit for client.

        Args:
            request: Incoming HTTP request
            call_next: Next middleware or route handler

        Returns:
            Response: HTTP response or rate limit error
        """
        # Get client IP
        client_ip = request.client.host if request.client else "unknown"

        # Get current time
        now = time.time()

        # Initialize client record
        if client_ip not in self.clients:
            self.clients[client_ip] = []

        # Remove old timestamps
        self.clients[client_ip] = [
            timestamp
            for timestamp in self.clients[client_ip]
            if now - timestamp < self.period
        ]

        # Check rate limit
        if len(self.clients[client_ip]) >= self.calls:
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "detail": f"Rate limit exceeded. Maximum {self.calls} requests per {self.period} seconds."
                },
                headers={
                    "Retry-After": str(self.period),
                    "X-RateLimit-Limit": str(self.calls),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(int(now + self.period)),
                },
            )

        # Record this request
        self.clients[client_ip].append(now)

        # Add rate limit headers to response
        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(self.calls)
        response.headers["X-RateLimit-Remaining"] = str(
            self.calls - len(self.clients[client_ip])
        )
        response.headers["X-RateLimit-Reset"] = str(
            int(self.clients[client_ip][0] + self.period)
        )

        return response
