"""Application configuration using Pydantic Settings."""
from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    APP_NAME: str = "Cat Canteen"
    ENVIRONMENT: Literal["development", "staging", "production"] = "development"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"

    # Database
    DATABASE_URL: str = Field(
        ...,
        description="PostgreSQL connection string",
        examples=["postgresql://user:password@localhost:5432/catcanteen"],
    )

    @property
    def async_database_url(self) -> str:
        """Get async-compatible database URL with asyncpg driver."""
        url = self.DATABASE_URL
        # Convert postgresql:// to postgresql+asyncpg://
        if url.startswith("postgresql://"):
            url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
        elif url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql+asyncpg://", 1)
        return url

    # JWT Authentication
    JWT_SECRET: str = Field(..., description="Secret key for JWT token generation")
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours

    # CORS
    allowed_origins_str: str = Field(
        default="http://localhost:5173,http://localhost:3000",
        validation_alias="ALLOWED_ORIGINS",
        exclude=True,  # Don't include in model dict
    )

    # Rate Limiting
    RATE_LIMIT_PUBLIC: int = 100  # requests per minute
    RATE_LIMIT_AUTHENTICATED: int = 1000  # requests per minute

    # File Upload
    MAX_UPLOAD_SIZE_MB: int = 10
    allowed_image_types_str: str = Field(
        default="image/jpeg,image/png,image/webp",
        validation_alias="ALLOWED_IMAGE_TYPES",
        exclude=True,  # Don't include in model dict
    )

    @property
    def ALLOWED_ORIGINS(self) -> list[str]:
        """Parse ALLOWED_ORIGINS from comma-separated string."""
        return [origin.strip() for origin in self.allowed_origins_str.split(",") if origin.strip()]

    @property
    def ALLOWED_IMAGE_TYPES(self) -> list[str]:
        """Parse ALLOWED_IMAGE_TYPES from comma-separated string."""
        return [img_type.strip() for img_type in self.allowed_image_types_str.split(",") if img_type.strip()]

    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.ENVIRONMENT == "production"

    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.ENVIRONMENT == "development"


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance.

    Returns:
        Settings: Application settings singleton.
    """
    return Settings()  # type: ignore


# Global settings instance
settings = get_settings()
