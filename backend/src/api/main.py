"""FastAPI main application entry point."""
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.api.v1.middleware import (
    CORSSecurityMiddleware,
    ErrorHandlingMiddleware,
    RateLimitMiddleware,
    RequestLoggingMiddleware,
)
from src.infrastructure.config import settings
from src.infrastructure.database.session import close_db, init_db


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan context manager.

    Handles startup and shutdown events.
    """
    # Startup
    print(f"🚀 Starting {settings.APP_NAME} API...")
    print(f"   Environment: {settings.ENVIRONMENT}")
    print(f"   Debug Mode: {settings.DEBUG}")

    # Initialize database (only in development)
    if settings.is_development:
        print("   Initializing database tables...")
        # await init_db()  # Commented out - use Alembic migrations instead

    yield

    # Shutdown
    print("🛑 Shutting down API...")
    await close_db()


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    description="可白牌化智慧餐飲訂單系統平台 - Backend API",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add custom middleware (order matters - first added = outermost)
app.add_middleware(ErrorHandlingMiddleware)
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(CORSSecurityMiddleware)

# Add rate limiting (only in production or if explicitly enabled)
if settings.is_production:
    app.add_middleware(
        RateLimitMiddleware,
        calls=settings.RATE_LIMIT_PUBLIC,
        period=60,
    )


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint for load balancers and monitoring.

    Returns:
        dict: Health status information
    """
    return JSONResponse(
        content={
            "status": "healthy",
            "environment": settings.ENVIRONMENT,
            "version": "0.1.0",
        }
    )


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information.

    Returns:
        dict: API information
    """
    return {
        "message": f"Welcome to {settings.APP_NAME} API",
        "version": "0.1.0",
        "docs": "/docs" if settings.DEBUG else "Documentation disabled in production",
    }


# Include API v1 routes
from src.api.v1.routes import ai, analytics, auth, brands, menus, orders

app.include_router(auth.router, prefix="/v1")
app.include_router(ai.router, prefix="/v1")
app.include_router(analytics.router, prefix="/v1")
app.include_router(brands.router, prefix="/v1")
app.include_router(menus.router, prefix="/v1")
app.include_router(orders.router, prefix="/v1")
