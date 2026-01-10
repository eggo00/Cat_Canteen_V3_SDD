"""ThemeEngine Domain Service.

Handles theme validation and color contrast checking.
"""
import re
from typing import Any

from src.domain.exceptions import ValidationError


class ThemeEngine:
    """Domain service for theme operations."""

    def validate_theme(self, theme_config: dict[str, Any]) -> bool:
        """Validate theme configuration.

        Args:
            theme_config: Theme configuration dictionary

        Returns:
            bool: True if valid

        Raises:
            ValidationError: If validation fails
        """
        if not isinstance(theme_config, dict):
            raise ValidationError("Theme configuration must be a dictionary")

        if "primaryColor" not in theme_config:
            raise ValidationError("Theme must contain 'primaryColor' field")

        # Validate all color fields
        color_fields = ["primaryColor", "secondaryColor", "accentColor"]
        for field in color_fields:
            if field in theme_config:
                color = theme_config[field]
                if not self._is_valid_hex_color(color):
                    raise ValidationError(
                        f"Invalid color format for {field}: {color}. "
                        "Must be HEX format (#RRGGBB)"
                    )

        return True

    @staticmethod
    def _is_valid_hex_color(color: str) -> bool:
        """Check if color is valid HEX format.

        Args:
            color: Color string to validate

        Returns:
            bool: True if valid HEX color
        """
        if not isinstance(color, str):
            return False

        hex_pattern = re.compile(r"^#[0-9A-Fa-f]{6}$")
        return bool(hex_pattern.match(color))

    def calculate_contrast(self, color1: str, color2: str) -> float:
        """Calculate contrast ratio between two colors.

        Uses WCAG 2.0 formula for contrast ratio calculation.

        Args:
            color1: First color in HEX format
            color2: Second color in HEX format

        Returns:
            float: Contrast ratio (1.0 to 21.0)

        References:
            https://www.w3.org/TR/WCAG20-TECHS/G17.html
        """
        luminance1 = self._calculate_luminance(color1)
        luminance2 = self._calculate_luminance(color2)

        # Ensure lighter color is in numerator
        lighter = max(luminance1, luminance2)
        darker = min(luminance1, luminance2)

        # WCAG contrast ratio formula
        contrast_ratio = (lighter + 0.05) / (darker + 0.05)

        return round(contrast_ratio, 2)

    @staticmethod
    def _calculate_luminance(hex_color: str) -> float:
        """Calculate relative luminance of a color.

        Args:
            hex_color: Color in HEX format (#RRGGBB)

        Returns:
            float: Relative luminance (0.0 to 1.0)
        """
        # Remove # and convert to RGB
        hex_color = hex_color.lstrip("#")
        r, g, b = tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))

        # Convert to 0-1 range
        r_srgb = r / 255.0
        g_srgb = g / 255.0
        b_srgb = b / 255.0

        # Apply sRGB to linear RGB conversion
        def to_linear(c: float) -> float:
            if c <= 0.03928:
                return c / 12.92
            else:
                return ((c + 0.055) / 1.055) ** 2.4

        r_linear = to_linear(r_srgb)
        g_linear = to_linear(g_srgb)
        b_linear = to_linear(b_srgb)

        # Calculate luminance using ITU-R BT.709 coefficients
        luminance = 0.2126 * r_linear + 0.7152 * g_linear + 0.0722 * b_linear

        return luminance
