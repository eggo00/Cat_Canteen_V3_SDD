"""Domain layer exceptions.

Common exceptions used across domain entities, services, and repositories.
"""


class DomainError(Exception):
    """Base exception for all domain errors."""

    pass


class ValidationError(DomainError, ValueError):
    """Raised when entity or value object validation fails."""

    pass


class NotFoundError(DomainError):
    """Raised when a requested entity is not found."""

    def __init__(self, entity_type: str, identifier: str) -> None:
        """Initialize NotFoundError.

        Args:
            entity_type: Type of entity (e.g., 'Brand', 'Category')
            identifier: Identifier used for lookup (e.g., ID, slug)
        """
        self.entity_type = entity_type
        self.identifier = identifier
        super().__init__(f"{entity_type} not found: {identifier}")


class DuplicateError(DomainError):
    """Raised when attempting to create a duplicate entity."""

    def __init__(self, entity_type: str, field: str, value: str) -> None:
        """Initialize DuplicateError.

        Args:
            entity_type: Type of entity (e.g., 'Brand')
            field: Field that has duplicate value (e.g., 'slug')
            value: Duplicate value
        """
        self.entity_type = entity_type
        self.field = field
        self.value = value
        super().__init__(f"{entity_type} with {field}='{value}' already exists")


class DuplicateSlugError(DuplicateError):
    """Raised when attempting to create a brand with duplicate slug."""

    def __init__(self, slug: str) -> None:
        """Initialize DuplicateSlugError.

        Args:
            slug: Duplicate slug value
        """
        super().__init__("Brand", "slug", slug)


class InvalidSlugError(ValidationError):
    """Raised when slug format is invalid."""

    def __init__(self, slug: str) -> None:
        """Initialize InvalidSlugError.

        Args:
            slug: Invalid slug value
        """
        super().__init__(
            f"Invalid slug format: '{slug}'. "
            "Slug must contain only lowercase letters, numbers, and hyphens."
        )


class InvalidColorError(ValidationError):
    """Raised when color format is invalid."""

    pass


class BusinessRuleViolationError(DomainError):
    """Raised when a business rule is violated."""

    pass
