"""ThemeConfig Value Object for brand theming.

This is an immutable value object that validates and stores theme configuration.
"""
import re
from dataclasses import dataclass
from typing import Any


class ValidationError(ValueError):
    """Raised when theme configuration validation fails."""

    pass


class InvalidColorError(ValidationError):
    """Raised when color format is invalid."""

    pass


class LowContrastError(ValidationError):
    """Raised when color contrast is too low for accessibility."""

    pass


@dataclass(frozen=True)
class ThemeConfig:
    """Immutable theme configuration value object.

    Validates and stores brand theme settings including colors and fonts.
    All colors must be in HEX format (#RRGGBB).
    """

    primary_color: str
    secondary_color: str | None = None
    accent_color: str | None = None
    font_family: str | None = None

    def __post_init__(self) -> None:
        """Validate theme configuration after initialization."""
        # Validate and normalize primary color (required)
        object.__setattr__(
            self, "primary_color", self._validate_and_normalize_color(self.primary_color)
        )

        # Validate and normalize optional colors
        if self.secondary_color:
            object.__setattr__(
                self,
                "secondary_color",
                self._validate_and_normalize_color(self.secondary_color),
            )

        if self.accent_color:
            object.__setattr__(
                self, "accent_color", self._validate_and_normalize_color(self.accent_color)
            )

        # Optional: Check color contrast for accessibility
        # This is a basic check - more sophisticated contrast checking can be added
        if self.secondary_color:
            self._check_contrast_warning(self.primary_color, self.secondary_color)

    @staticmethod
    def _validate_and_normalize_color(color: str) -> str:
        """Validate HEX color format and normalize to uppercase.

        Args:
            color: Color string to validate

        Returns:
            str: Normalized color in uppercase HEX format

        Raises:
            InvalidColorError: If color format is invalid
        """
        if not color:
            raise InvalidColorError("Color cannot be empty")

        # HEX color pattern: #RRGGBB (case insensitive)
        hex_pattern = re.compile(r"^#[0-9A-Fa-f]{6}$")

        if not hex_pattern.match(color):
            raise InvalidColorError(
                f"Invalid color format: {color}. Must be HEX format (#RRGGBB)"
            )

        # Normalize to uppercase
        return color.upper()

    @staticmethod
    def _check_contrast_warning(color1: str, color2: str) -> None:
        """Check if two colors have sufficient contrast.

        This is a simplified check. Raises warning for very similar colors.

        Args:
            color1: First color in HEX format
            color2: Second color in HEX format

        Raises:
            LowContrastError: If colors are too similar
        """
        # Remove # and convert to RGB
        def hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
            hex_color = hex_color.lstrip("#")
            return tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))  # type: ignore

        rgb1 = hex_to_rgb(color1)
        rgb2 = hex_to_rgb(color2)

        # Calculate simple color difference
        diff = sum(abs(c1 - c2) for c1, c2 in zip(rgb1, rgb2))

        # If colors are extremely similar (difference < 30), raise error
        if diff < 30:
            raise LowContrastError(
                f"Colors {color1} and {color2} are too similar. "
                "This may cause accessibility issues."
            )

    def to_dict(self) -> dict[str, Any]:
        """Convert ThemeConfig to dictionary (camelCase keys for API).

        Returns:
            dict: Theme configuration as dictionary
        """
        result: dict[str, Any] = {
            "primaryColor": self.primary_color,
        }

        if self.secondary_color:
            result["secondaryColor"] = self.secondary_color

        if self.accent_color:
            result["accentColor"] = self.accent_color

        if self.font_family:
            result["fontFamily"] = self.font_family

        return result

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ThemeConfig":
        """Create ThemeConfig from dictionary (camelCase keys from API).

        Args:
            data: Dictionary with theme configuration

        Returns:
            ThemeConfig: New ThemeConfig instance

        Raises:
            ValidationError: If required fields are missing
        """
        if "primaryColor" not in data:
            raise ValidationError("primaryColor is required in theme configuration")

        return cls(
            primary_color=data["primaryColor"],
            secondary_color=data.get("secondaryColor"),
            accent_color=data.get("accentColor"),
            font_family=data.get("fontFamily"),
        )

    def __eq__(self, other: object) -> bool:
        """Compare two ThemeConfig objects for equality.

        Args:
            other: Other object to compare

        Returns:
            bool: True if all fields are equal
        """
        if not isinstance(other, ThemeConfig):
            return False

        return (
            self.primary_color == other.primary_color
            and self.secondary_color == other.secondary_color
            and self.accent_color == other.accent_color
            and self.font_family == other.font_family
        )
