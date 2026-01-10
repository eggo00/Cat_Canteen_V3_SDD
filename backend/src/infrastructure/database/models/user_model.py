"""SQLAlchemy model for User entity."""
from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin, UUIDMixin


class UserModel(Base, UUIDMixin, TimestampMixin):
    """User model for authentication and authorization."""

    __tablename__ = "users"

    # Authentication
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)

    # User Information
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)

    # Role-Based Access Control
    role: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="customer",
        index=True,
        comment="customer, staff, admin, super_admin",
    )

    # Brand Association (NULL for super_admin and customer)
    brand_id: Mapped[UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("brands.id", ondelete="SET NULL"), nullable=True, index=True
    )

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    # Relationships
    brand: Mapped["BrandModel | None"] = relationship("BrandModel", back_populates="users")

    def __repr__(self) -> str:
        """String representation of User."""
        return f"<User(id={self.id}, email={self.email}, role={self.role})>"
