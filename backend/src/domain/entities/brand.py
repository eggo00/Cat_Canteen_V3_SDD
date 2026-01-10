"""Brand Entity - Domain Model.

Represents a restaurant brand in the white-label ordering system.
"""
import re
from uuid import UUID, uuid4

from src.domain.exceptions import InvalidSlugError, ValidationError
from src.domain.value_objects.theme_config import ThemeConfig


class Brand:
    """Brand entity representing a restaurant brand.

    A brand represents a unique restaurant or food service business
    with its own visual identity (theme) and menu.
    """

    def __init__(
        self,
        name: str,
        slug: str,
        theme_config: dict | ThemeConfig,
        id: UUID | None = None,
        description: str | None = None,
        logo_url: str | None = None,
        is_active: bool = True,
    ):
        """Initialize a Brand entity.

        Args:
            name: Brand name (required, max 255 chars)
            slug: URL-safe identifier (required, max 255 chars)
            theme_config: Theme configuration (ThemeConfig or dict)
            id: Unique identifier (auto-generated if not provided)
            description: Brand description (optional)
            logo_url: URL to brand logo image (optional)
            is_active: Whether brand is currently active (default: True)

        Raises:
            ValidationError: If validation fails
        """
        # Validate required fields
        if not name or not name.strip():
            raise ValidationError("Brand name is required")

        if not slug or not slug.strip():
            raise ValidationError("Brand slug is required")

        # Validate max lengths
        if len(name) > 255:
            raise ValidationError(f"Brand name too long (max 255 characters, got {len(name)})")

        if len(slug) > 255:
            raise ValidationError(f"Brand slug too long (max 255 characters, got {len(slug)})")

        # Convert theme_config to ThemeConfig if it's a dict
        if isinstance(theme_config, dict):
            theme_config = ThemeConfig.from_dict(theme_config)

        if not isinstance(theme_config, ThemeConfig):
            raise ValidationError("theme_config must be a ThemeConfig object or dict")

        # Validate and normalize slug
        normalized_slug = self._validate_and_normalize_slug(slug)

        # Set attributes
        self.id = id or uuid4()
        self.name = name.strip()
        self.slug = normalized_slug
        self.description = description
        self.logo_url = logo_url
        self.theme_config = theme_config
        self.is_active = is_active

    @staticmethod
    def _validate_and_normalize_slug(slug: str) -> str:
        """Validate and normalize brand slug.

        Slug must contain only lowercase letters, numbers, and hyphens.

        Args:
            slug: Slug to validate

        Returns:
            str: Normalized slug (lowercase)

        Raises:
            InvalidSlugError: If slug contains invalid characters
        """
        # Convert to lowercase
        normalized = slug.lower().strip()

        # Slug pattern: lowercase letters, numbers, hyphens only
        if not re.match(r"^[a-z0-9-]+$", normalized):
            raise InvalidSlugError(
                f"Invalid slug format: '{slug}'. "
                "Slug must contain only lowercase letters, numbers, and hyphens."
            )

        return normalized

    def activate(self) -> None:
        """Activate the brand."""
        self.is_active = True

    def deactivate(self) -> None:
        """Deactivate the brand."""
        self.is_active = False

    def update_theme(self, theme_config: dict | ThemeConfig) -> None:
        """Update brand theme configuration.

        Args:
            theme_config: New theme configuration

        Raises:
            ValidationError: If theme validation fails
        """
        if isinstance(theme_config, dict):
            theme_config = ThemeConfig.from_dict(theme_config)

        if not isinstance(theme_config, ThemeConfig):
            raise ValidationError("theme_config must be a ThemeConfig object or dict")

        self.theme_config = theme_config

    def __repr__(self) -> str:
        """String representation of Brand."""
        return f"<Brand(id={self.id}, name={self.name}, slug={self.slug}, active={self.is_active})>"

    def __eq__(self, other: object) -> bool:
        """Compare two brands for equality (by ID).

        Args:
            other: Other object to compare

        Returns:
            bool: True if IDs are equal
        """
        if not isinstance(other, Brand):
            return False
        return self.id == other.id
