"""MenuRepository implementation using SQLAlchemy.

Provides persistence for Menu entities (Category, MenuItem, CustomizationOption).
"""
from decimal import Decimal
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.domain.entities.category import Category
from src.domain.entities.customization_option import CustomizationOption
from src.domain.entities.menu_item import MenuItem
from src.domain.repositories.menu_repository import MenuRepository
from src.infrastructure.database.models.menu_model import (
    CategoryModel,
    CustomizationOptionModel,
    MenuItemModel,
)


class MenuRepositoryImpl(MenuRepository):
    """SQLAlchemy implementation of MenuRepository."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize repository.

        Args:
            session: Async SQLAlchemy session
        """
        self.session = session

    async def create_category(
        self, brand_id: UUID, category: Category
    ) -> Category:
        """Create a new category for a brand.

        Args:
            brand_id: Brand UUID
            category: Category entity to create

        Returns:
            Created category with generated ID
        """
        # Convert entity to model
        category_model = CategoryModel(
            id=category.id,
            brand_id=brand_id,
            name=category.name,
            description=category.description,
            display_order=category.display_order,
            is_active=True,
        )

        self.session.add(category_model)
        await self.session.flush()
        await self.session.refresh(category_model)

        # Convert model back to entity
        return self._category_to_entity(category_model, include_items=False)

    async def get_category_by_id(self, category_id: UUID) -> Category | None:
        """Get category by ID.

        Args:
            category_id: Category UUID

        Returns:
            Category if found, None otherwise
        """
        stmt = (
            select(CategoryModel)
            .where(CategoryModel.id == category_id)
            .options(
                selectinload(CategoryModel.menu_items).selectinload(
                    MenuItemModel.customization_options
                )
            )
        )
        result = await self.session.execute(stmt)
        category_model = result.scalar_one_or_none()

        if category_model is None:
            return None

        return self._category_to_entity(category_model, include_items=True)

    async def get_categories_by_brand(
        self, brand_id: UUID, include_items: bool = True
    ) -> list[Category]:
        """Get all categories for a brand.

        Args:
            brand_id: Brand UUID
            include_items: Whether to include menu items

        Returns:
            List of categories ordered by display_order
        """
        stmt = (
            select(CategoryModel)
            .where(CategoryModel.brand_id == brand_id)
            .order_by(CategoryModel.display_order)
        )

        if include_items:
            stmt = stmt.options(
                selectinload(CategoryModel.menu_items).selectinload(
                    MenuItemModel.customization_options
                )
            )

        result = await self.session.execute(stmt)
        category_models = result.scalars().all()

        return [
            self._category_to_entity(model, include_items=include_items)
            for model in category_models
        ]

    async def update_category(self, category: Category) -> Category:
        """Update an existing category.

        Args:
            category: Category entity with updated data

        Returns:
            Updated category

        Raises:
            NotFoundError: If category not found
        """
        stmt = select(CategoryModel).where(CategoryModel.id == category.id)
        result = await self.session.execute(stmt)
        category_model = result.scalar_one_or_none()

        if category_model is None:
            from src.domain.exceptions import NotFoundError

            raise NotFoundError("Category", str(category.id))

        # Update model fields
        category_model.name = category.name
        category_model.description = category.description
        category_model.display_order = category.display_order

        await self.session.flush()
        await self.session.refresh(category_model)

        return self._category_to_entity(category_model, include_items=False)

    async def delete_category(self, category_id: UUID) -> bool:
        """Delete a category by ID.

        Args:
            category_id: Category UUID

        Returns:
            True if deleted, False if not found
        """
        stmt = select(CategoryModel).where(CategoryModel.id == category_id)
        result = await self.session.execute(stmt)
        category_model = result.scalar_one_or_none()

        if category_model is None:
            return False

        await self.session.delete(category_model)
        await self.session.flush()

        return True

    async def upload_menu_json(self, brand_id: UUID, menu_data: dict) -> list[Category]:
        """Upload complete menu from JSON data.

        This method replaces all existing categories and menu items
        for the brand with the new data from JSON.

        Args:
            brand_id: Brand UUID
            menu_data: Menu data in JSON format (validated by MenuEngine)

        Returns:
            List of created categories with items
        """
        # Delete all existing categories for this brand
        # (CASCADE will delete menu_items and customization_options)
        delete_stmt = delete(CategoryModel).where(CategoryModel.brand_id == brand_id)
        await self.session.execute(delete_stmt)
        await self.session.flush()

        # Create new categories from JSON
        categories = []
        for category_data in menu_data.get("categories", []):
            # Create category
            category = Category(
                name=category_data["name"],
                description=category_data.get("description"),
                display_order=category_data["display_order"],
            )

            # Create category model
            category_model = CategoryModel(
                id=category.id,
                brand_id=brand_id,
                name=category.name,
                description=category.description,
                display_order=category.display_order,
                is_active=True,
            )
            self.session.add(category_model)

            # Create menu items
            menu_items = []
            for item_data in category_data.get("menuItems", []):
                menu_item = MenuItem(
                    name=item_data["name"],
                    description=item_data.get("description"),
                    price=float(item_data["price"]),
                    display_order=item_data["display_order"],
                )

                # Create menu item model
                menu_item_model = MenuItemModel(
                    id=menu_item.id,
                    category_id=category.id,
                    name=menu_item.name,
                    description=menu_item.description,
                    price=Decimal(str(menu_item.price)),
                    display_order=menu_item.display_order,
                    is_available=True,
                )
                self.session.add(menu_item_model)

                # Create customization options if present
                customization_options = []
                for option_data in item_data.get("customizationOptions", []):
                    option = CustomizationOption(
                        option_type=option_data["option_type"],
                        name=option_data["name"],
                        price_adjustment=float(option_data["price_adjustment"]),
                    )

                    # Create customization option model
                    option_model = CustomizationOptionModel(
                        id=option.id,
                        menu_item_id=menu_item.id,
                        option_type=option.option_type,
                        name=option.name,
                        price_adjustment=Decimal(str(option.price_adjustment)),
                        constraints=option_data.get("constraints"),
                        display_order=option_data.get("display_order", 0),
                    )
                    self.session.add(option_model)
                    customization_options.append(option)

                menu_item.customization_options = customization_options
                menu_items.append(menu_item)

            category.menu_items = menu_items
            categories.append(category)

        await self.session.flush()

        return categories

    async def get_full_menu(self, brand_id: UUID) -> dict:
        """Get complete menu as JSON for a brand.

        Args:
            brand_id: Brand UUID

        Returns:
            Menu data in JSON format with all categories and items
        """
        # Get all categories with items
        categories = await self.get_categories_by_brand(brand_id, include_items=True)

        # Convert to JSON format
        categories_json = []
        for category in categories:
            menu_items_json = []
            for item in category.menu_items:
                customization_options_json = [
                    {
                        "id": str(option.id),
                        "option_type": option.option_type,
                        "name": option.name,
                        "price_adjustment": float(option.price_adjustment),
                    }
                    for option in item.customization_options
                ]

                menu_items_json.append(
                    {
                        "id": str(item.id),
                        "name": item.name,
                        "description": item.description,
                        "price": float(item.price),
                        "display_order": item.display_order,
                        "customizationOptions": customization_options_json,
                    }
                )

            categories_json.append(
                {
                    "id": str(category.id),
                    "name": category.name,
                    "description": category.description,
                    "display_order": category.display_order,
                    "menuItems": menu_items_json,
                }
            )

        return {"categories": categories_json}

    async def reorder_categories(
        self, brand_id: UUID, category_order: list[UUID]
    ) -> bool:
        """Reorder categories for a brand.

        Args:
            brand_id: Brand UUID
            category_order: List of category IDs in desired order

        Returns:
            True if successful

        Raises:
            NotFoundError: If brand or any category not found
            ValidationError: If category list is invalid
        """
        # Get all categories for the brand
        stmt = select(CategoryModel).where(CategoryModel.brand_id == brand_id)
        result = await self.session.execute(stmt)
        category_models = result.scalars().all()

        # Validate that all categories exist
        existing_ids = {model.id for model in category_models}
        provided_ids = set(category_order)

        if existing_ids != provided_ids:
            from src.domain.exceptions import ValidationError

            raise ValidationError(
                "Category order list doesn't match existing categories"
            )

        # Update display_order for each category
        for order, category_id in enumerate(category_order):
            stmt = select(CategoryModel).where(CategoryModel.id == category_id)
            result = await self.session.execute(stmt)
            category_model = result.scalar_one_or_none()
            if category_model:
                category_model.display_order = order

        await self.session.flush()

        return True

    def _category_to_entity(
        self, model: CategoryModel, include_items: bool = True
    ) -> Category:
        """Convert CategoryModel to Category entity.

        Args:
            model: CategoryModel instance
            include_items: Whether to include menu items

        Returns:
            Category entity
        """
        menu_items = []
        if include_items and model.menu_items:
            menu_items = [
                self._menu_item_to_entity(item_model)
                for item_model in sorted(
                    model.menu_items, key=lambda x: x.display_order
                )
            ]

        return Category(
            id=model.id,
            name=model.name,
            description=model.description,
            display_order=model.display_order,
            menu_items=menu_items,
        )

    def _menu_item_to_entity(self, model: MenuItemModel) -> MenuItem:
        """Convert MenuItemModel to MenuItem entity.

        Args:
            model: MenuItemModel instance

        Returns:
            MenuItem entity
        """
        customization_options = []
        if model.customization_options:
            customization_options = [
                self._customization_option_to_entity(option_model)
                for option_model in sorted(
                    model.customization_options, key=lambda x: x.display_order
                )
            ]

        return MenuItem(
            id=model.id,
            name=model.name,
            description=model.description,
            price=float(model.price),
            display_order=model.display_order,
            customization_options=customization_options,
        )

    def _customization_option_to_entity(
        self, model: CustomizationOptionModel
    ) -> CustomizationOption:
        """Convert CustomizationOptionModel to CustomizationOption entity.

        Args:
            model: CustomizationOptionModel instance

        Returns:
            CustomizationOption entity
        """
        return CustomizationOption(
            id=model.id,
            option_type=model.option_type,
            name=model.name,
            price_adjustment=float(model.price_adjustment),
        )
