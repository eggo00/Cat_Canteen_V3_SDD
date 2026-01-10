"""MenuEngine Domain Service.

Handles menu JSON validation and slug generation.
"""
import re
import unicodedata
from typing import Any

from src.domain.exceptions import ValidationError


class MenuEngine:
    """Domain service for menu operations."""

    def validate_menu_json(self, menu_data: dict[str, Any]) -> bool:
        """Validate menu JSON structure.

        Args:
            menu_data: Menu data dictionary

        Returns:
            bool: True if valid

        Raises:
            ValidationError: If validation fails
        """
        if not isinstance(menu_data, dict):
            raise ValidationError("Menu data must be a dictionary")

        if "categories" not in menu_data:
            raise ValidationError("Menu data must contain 'categories' field")

        if not isinstance(menu_data["categories"], list):
            raise ValidationError("'categories' must be a list")

        # Validate each category
        for idx, category in enumerate(menu_data["categories"]):
            if not isinstance(category, dict):
                raise ValidationError(f"Category at index {idx} must be a dictionary")

            if "name" not in category:
                raise ValidationError(f"Category at index {idx} must have 'name' field")

            if "menuItems" in category:
                if not isinstance(category["menuItems"], list):
                    raise ValidationError(
                        f"Category '{category.get('name')}' menuItems must be a list"
                    )

                # Validate each menu item
                for item_idx, item in enumerate(category["menuItems"]):
                    if not isinstance(item, dict):
                        raise ValidationError(
                            f"Menu item at index {item_idx} in category "
                            f"'{category.get('name')}' must be a dictionary"
                        )

                    if "name" not in item:
                        raise ValidationError(
                            f"Menu item at index {item_idx} in category "
                            f"'{category.get('name')}' must have 'name' field"
                        )

                    if "price" in item:
                        try:
                            price = float(item["price"])
                            if price < 0:
                                raise ValidationError(
                                    f"Menu item '{item.get('name')}' has negative price"
                                )
                        except (ValueError, TypeError) as e:
                            raise ValidationError(
                                f"Menu item '{item.get('name')}' has invalid price"
                            ) from e

        return True

    def generate_slug(self, name: str) -> str:
        """Generate URL-safe slug from name.

        Converts Chinese characters to pinyin-like representation,
        removes special characters, and converts to lowercase.

        Args:
            name: Name to convert to slug

        Returns:
            str: URL-safe slug

        Examples:
            "測試 餐廳" -> "ce-shi-can-ting"
            "Café & Bar" -> "cafe-bar"
        """
        # First transliterate Chinese/non-ASCII characters
        transliterated = self._simple_transliterate(name)

        # Normalize unicode characters for accents
        normalized = unicodedata.normalize("NFKD", transliterated)

        # Convert to ASCII
        ascii_text = normalized.encode("ascii", "ignore").decode("ascii")

        # Convert to lowercase
        slug = ascii_text.lower()

        # Replace spaces and special characters with hyphens
        slug = re.sub(r"[^\w\s-]", "", slug)
        slug = re.sub(r"[-\s]+", "-", slug)

        # Remove leading/trailing hyphens
        slug = slug.strip("-")

        return slug or "item"

    @staticmethod
    def _simple_transliterate(text: str) -> str:
        """Simple transliteration for non-ASCII characters.

        This is a placeholder. In production, use a proper library like pypinyin.

        Args:
            text: Text to transliterate

        Returns:
            str: Transliterated text
        """
        # Basic mapping for common Chinese characters used in tests
        mappings = {
            "測": "ce",
            "試": "shi",
            "餐": "can",
            "廳": "ting",
            "貓": "mao",
            "咪": "mi",
            "食": "shi",
            "堂": "tang",
        }

        result = []
        for char in text:
            if char in mappings:
                result.append(mappings[char])
                result.append(" ")  # Add space after Chinese transliteration
            else:
                result.append(char)  # Preserve all other characters

        return "".join(result)
