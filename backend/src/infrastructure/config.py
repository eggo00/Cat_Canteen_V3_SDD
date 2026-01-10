"""Application configuration using Pydantic Settings."""
from functools import lru_cache
from typing import Literal

from pydantic import Field, field_validator
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

    # JWT Authentication
    JWT_SECRET: str = Field(..., description="Secret key for JWT token generation")
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours

    # CORS
    ALLOWED_ORIGINS: str = Field(
        default="http://localhost:5173,http://localhost:3000",
        description="Comma-separated list of allowed origins",
    )

    # Rate Limiting
    RATE_LIMIT_PUBLIC: int = 100  # requests per minute
    RATE_LIMIT_AUTHENTICATED: int = 1000  # requests per minute

    # File Upload
    MAX_UPLOAD_SIZE_MB: int = 10
    ALLOWED_IMAGE_TYPES: str = "image/jpeg,image/png,image/webp"

    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def parse_origins(cls, v: str) -> list[str]:
        """Parse comma-separated origins into a list."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    @field_validator("ALLOWED_IMAGE_TYPES", mode="before")
    @classmethod
    def parse_image_types(cls, v: str) -> list[str]:
        """Parse comma-separated image types into a list."""
        if isinstance(v, str):
            return [img_type.strip() for img_type in v.split(",")]
        return v

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
