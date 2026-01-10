"""CustomizationOption entity.

Represents a customization option for menu items (e.g., size, sweetness level).
"""
from uuid import UUID, uuid4

from src.domain.exceptions import ValidationError


class CustomizationOption:
    """Customization option entity for menu items."""

    def __init__(
        self,
        option_type: str,
        name: str,
        price_adjustment: float,
        id: UUID | None = None,
    ) -> None:
        """Initialize customization option.

        Args:
            option_type: Type of option (e.g., 'size', 'sweetness', 'ice')
            name: Display name of the option (e.g., '大杯', '半糖')
            price_adjustment: Price adjustment (can be positive, zero, or negative)
            id: Unique identifier (auto-generated if not provided)

        Raises:
            ValidationError: If validation fails
        """
        # Validate name
        if not name or not name.strip():
            raise ValidationError("Customization option name cannot be empty")

        if len(name) > 100:
            raise ValidationError(
                f"Customization option name cannot exceed 100 characters (got {len(name)})"
            )

        # Set attributes
        self.id = id or uuid4()
        self.option_type = option_type
        self.name = name
        self.price_adjustment = price_adjustment

    def __eq__(self, other: object) -> bool:
        """Check equality based on ID."""
        if not isinstance(other, CustomizationOption):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        """Return hash based on ID."""
        return hash(self.id)

    def __repr__(self) -> str:
        """Return string representation."""
        return (
            f"CustomizationOption(id={self.id}, option_type='{self.option_type}', "
            f"name='{self.name}', price_adjustment={self.price_adjustment})"
        )
