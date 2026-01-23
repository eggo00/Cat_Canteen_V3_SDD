"""FastAPI main application entry point."""
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.api.v1.middleware import (
    CORSSecurityMiddleware,
    ErrorHandlingMiddleware,
    RateLimitMiddleware,
    RequestLoggingMiddleware,
)
from src.api.v1.routes import ai, analytics, auth, brands, menus, orders
from src.infrastructure.config import settings
from src.infrastructure.database.session import close_db


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
async def health_check() -> JSONResponse:
    """Health check endpoint for load balancers and monitoring.

    Returns:
        JSONResponse: Health status information
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
async def root() -> dict[str, Any]:
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
app.include_router(auth.router, prefix="/v1")
app.include_router(ai.router, prefix="/v1")
app.include_router(analytics.router, prefix="/v1")
app.include_router(brands.router, prefix="/v1")
app.include_router(menus.router, prefix="/v1")
app.include_router(orders.router, prefix="/v1")


# Seed endpoint for initial data setup
@app.post("/seed", tags=["Setup"])
async def seed_database() -> dict[str, Any]:
    """Create initial admin user and demo data.

    This endpoint can only be used once to bootstrap the database.
    It will create:
    - Super admin user (admin@catcanteen.com / Admin123!)
    - Demo brand with menu items

    Returns:
        dict: Seed result information
    """
    from uuid import uuid4
    from sqlalchemy import text
    from src.infrastructure.database.session import AsyncSessionLocal
    from src.infrastructure.auth.password_hasher import PasswordHasher

    results = {"created": [], "skipped": []}

    async with AsyncSessionLocal() as session:
        # Check if admin already exists
        result = await session.execute(
            text("SELECT id FROM users WHERE email = 'admin@catcanteen.com'")
        )
        if result.fetchone():
            results["skipped"].append("Admin user already exists")
        else:
            # Create admin user
            admin_id = uuid4()
            password_hash = PasswordHasher.hash("Admin123!")

            await session.execute(
                text("""
                    INSERT INTO users (id, email, password_hash, full_name, role, is_active)
                    VALUES (:id, :email, :password_hash, :name, :role, TRUE)
                """),
                {
                    "id": admin_id,
                    "email": "admin@catcanteen.com",
                    "password_hash": password_hash,
                    "name": "Super Admin",
                    "role": "super_admin",
                }
            )
            results["created"].append("Admin user: admin@catcanteen.com / Admin123!")

        # Check if demo brand exists
        result = await session.execute(
            text("SELECT id FROM brands WHERE slug = 'demo-cafe'")
        )
        brand_row = result.fetchone()

        if brand_row:
            results["skipped"].append("Demo brand already exists")
        else:
            # Create demo brand
            brand_id = uuid4()
            await session.execute(
                text("""
                    INSERT INTO brands (id, name, slug, description, primary_color, secondary_color)
                    VALUES (:id, :name, :slug, :description, :primary_color, :secondary_color)
                """),
                {
                    "id": brand_id,
                    "name": "Demo Cafe",
                    "slug": "demo-cafe",
                    "description": "歡迎來到 Demo Cafe！我們提供各式精選咖啡和輕食。",
                    "primary_color": "#8B4513",
                    "secondary_color": "#D2691E",
                }
            )
            results["created"].append("Demo brand: demo-cafe")

            # Create categories
            drinks_id = uuid4()
            food_id = uuid4()
            desserts_id = uuid4()

            await session.execute(
                text("""
                    INSERT INTO categories (id, brand_id, name, description, display_order)
                    VALUES
                        (:drinks_id, :brand_id, '飲品', '各式咖啡和茶飲', 1),
                        (:food_id, :brand_id, '輕食', '三明治和沙拉', 2),
                        (:desserts_id, :brand_id, '甜點', '蛋糕和點心', 3)
                """),
                {
                    "drinks_id": drinks_id,
                    "food_id": food_id,
                    "desserts_id": desserts_id,
                    "brand_id": brand_id,
                }
            )
            results["created"].append("Categories: 飲品, 輕食, 甜點")

            # Create menu items
            menu_items = [
                (uuid4(), drinks_id, "美式咖啡", "經典美式，香醇濃郁", 60, True),
                (uuid4(), drinks_id, "拿鐵咖啡", "濃郁咖啡配上綿密奶泡", 80, True),
                (uuid4(), drinks_id, "卡布奇諾", "義式經典，奶泡豐富", 85, False),
                (uuid4(), drinks_id, "抹茶拿鐵", "日式抹茶與牛奶的完美結合", 90, True),
                (uuid4(), drinks_id, "紅茶拿鐵", "錫蘭紅茶配上鮮奶", 75, False),
                (uuid4(), food_id, "火腿起司三明治", "經典組合，滿足一整天", 120, True),
                (uuid4(), food_id, "燻鮭魚貝果", "新鮮燻鮭魚配奶油起司", 150, False),
                (uuid4(), food_id, "凱薩沙拉", "羅蔓生菜配帕瑪森起司", 130, False),
                (uuid4(), desserts_id, "提拉米蘇", "義式經典甜點", 120, True),
                (uuid4(), desserts_id, "紐約起司蛋糕", "濃郁起司香", 110, False),
                (uuid4(), desserts_id, "巧克力布朗尼", "濃厚巧克力風味", 90, True),
            ]

            for item_id, cat_id, name, desc, price, is_popular in menu_items:
                await session.execute(
                    text("""
                        INSERT INTO menu_items (id, category_id, name, description, price, is_popular, is_available)
                        VALUES (:id, :category_id, :name, :description, :price, :is_popular, TRUE)
                    """),
                    {
                        "id": item_id,
                        "category_id": cat_id,
                        "name": name,
                        "description": desc,
                        "price": price,
                        "is_popular": is_popular,
                    }
                )
            results["created"].append(f"Menu items: {len(menu_items)} items")

        await session.commit()

    return {
        "status": "success",
        "results": results,
        "demo_url": "/demo-cafe/menu",
        "admin_credentials": {
            "email": "admin@catcanteen.com",
            "password": "Admin123!"
        }
    }
