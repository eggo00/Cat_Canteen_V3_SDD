"""Pytest configuration and fixtures for all tests."""
import asyncio
from typing import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import Session, sessionmaker

from src.infrastructure.database.models import Base

# Test database URL (use SQLite for fast tests)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
TEST_SYNC_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
def sync_engine():
    """Create sync SQLAlchemy engine for testing."""
    engine = create_engine(TEST_SYNC_DATABASE_URL, echo=False)
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture(scope="function")
def sync_session(sync_engine) -> Generator[Session, None, None]:
    """Create sync database session for testing."""
    SessionLocal = sessionmaker(bind=sync_engine, autocommit=False, autoflush=False)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest_asyncio.fixture(scope="function")
async def async_engine():
    """Create async SQLAlchemy engine for testing."""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def async_session(async_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create async database session for testing."""
    AsyncSessionLocal = async_sessionmaker(
        bind=async_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )

    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.rollback()
            await session.close()


@pytest.fixture
def sample_brand_data() -> dict:
    """Sample brand data for testing."""
    return {
        "name": "測試餐廳",
        "slug": "test-restaurant",
        "description": "這是一個測試餐廳",
        "logo_url": "https://example.com/logo.png",
        "theme_config": {
            "primaryColor": "#FF6B6B",
            "secondaryColor": "#4ECDC4",
            "fontFamily": "Noto Sans TC",
        },
        "is_active": True,
    }


@pytest.fixture
def sample_menu_data() -> dict:
    """Sample menu data for testing."""
    return {
        "categories": [
            {
                "name": "飲料",
                "description": "各式飲品",
                "display_order": 1,
                "menuItems": [
                    {
                        "name": "美式咖啡",
                        "description": "香醇美式咖啡",
                        "price": 100.00,
                        "display_order": 1,
                        "customizationOptions": [
                            {
                                "optionType": "size",
                                "name": "大杯",
                                "priceAdjustment": 20.00,
                            },
                            {
                                "optionType": "sweetness",
                                "name": "半糖",
                                "priceAdjustment": 0.00,
                            },
                        ],
                    }
                ],
            }
        ]
    }


@pytest.fixture
def sample_theme_config() -> dict:
    """Sample theme configuration for testing."""
    return {
        "primaryColor": "#FF6B6B",
        "secondaryColor": "#4ECDC4",
        "accentColor": "#FFE66D",
        "fontFamily": "Noto Sans TC",
    }
