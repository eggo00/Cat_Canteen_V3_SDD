"""SQLAlchemy model for Brand entity."""
from sqlalchemy import Boolean, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin, UUIDMixin


class BrandModel(Base, UUIDMixin, TimestampMixin):
    """Brand model representing a restaurant brand in the white-label system."""

    __tablename__ = "brands"

    # Basic Information
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    slug: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Visual Identity
    logo_url: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    theme_config: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
        comment="Theme configuration (colors, fonts, etc.)",
    )

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    # Relationships
    categories: Mapped[list["CategoryModel"]] = relationship(
        "CategoryModel", back_populates="brand", cascade="all, delete-orphan"
    )
    orders: Mapped[list["OrderModel"]] = relationship(
        "OrderModel", back_populates="brand", cascade="all, delete-orphan"
    )
    users: Mapped[list["UserModel"]] = relationship(
        "UserModel", back_populates="brand", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        """String representation of Brand."""
        return f"<Brand(id={self.id}, name={self.name}, slug={self.slug})>"
