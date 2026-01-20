"""UserRepository implementation using SQLAlchemy.

Provides persistence for User entities.
"""
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.user import User, UserRole
from src.domain.exceptions import DuplicateEmailError, NotFoundError
from src.domain.repositories.user_repository import UserRepository
from src.infrastructure.database.models.user_model import UserModel


class UserRepositoryImpl(UserRepository):
    """SQLAlchemy implementation of UserRepository."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize repository.

        Args:
            session: Async SQLAlchemy session
        """
        self.session = session

    async def create(self, user: User) -> User:
        """Create a new user.

        Args:
            user: User entity to create

        Returns:
            Created user with database-generated fields

        Raises:
            DuplicateEmailError: If email already exists
        """
        # Check for duplicate email
        if await self.exists_by_email(user.email):
            raise DuplicateEmailError(user.email)

        # Convert entity to model
        user_model = UserModel(
            id=user.id,
            email=user.email,
            password_hash=user.password_hash,
            full_name=user.name or "",  # Model uses full_name
            role=user.role.value,
            brand_id=user.brand_id,
            is_active=user.is_active,
        )

        self.session.add(user_model)
        await self.session.flush()
        await self.session.refresh(user_model)

        # Convert model back to entity
        return self._to_entity(user_model)

    async def get_by_id(self, user_id: UUID) -> User | None:
        """Get user by ID.

        Args:
            user_id: User UUID

        Returns:
            User if found, None otherwise
        """
        stmt = select(UserModel).where(UserModel.id == user_id)
        result = await self.session.execute(stmt)
        user_model = result.scalar_one_or_none()

        if user_model is None:
            return None

        return self._to_entity(user_model)

    async def get_by_email(self, email: str) -> User | None:
        """Get user by email address.

        Args:
            email: User email address

        Returns:
            User if found, None otherwise
        """
        email = email.strip().lower()
        stmt = select(UserModel).where(UserModel.email == email)
        result = await self.session.execute(stmt)
        user_model = result.scalar_one_or_none()

        if user_model is None:
            return None

        return self._to_entity(user_model)

    async def get_by_brand(
        self,
        brand_id: UUID,
        skip: int = 0,
        limit: int = 100,
        role: UserRole | None = None,
    ) -> list[User]:
        """Get users belonging to a specific brand.

        Args:
            brand_id: Brand UUID to filter by
            skip: Number of records to skip
            limit: Maximum number of records to return
            role: Optional role filter

        Returns:
            List of users for the brand
        """
        stmt = select(UserModel).where(UserModel.brand_id == brand_id)

        if role:
            stmt = stmt.where(UserModel.role == role.value)

        stmt = stmt.offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        user_models = result.scalars().all()

        return [self._to_entity(model) for model in user_models]

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        role: UserRole | None = None,
        is_active: bool | None = None,
    ) -> list[User]:
        """Get all users with pagination and optional filters.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            role: Optional role filter
            is_active: Optional active status filter

        Returns:
            List of users
        """
        stmt = select(UserModel)

        if role:
            stmt = stmt.where(UserModel.role == role.value)

        if is_active is not None:
            stmt = stmt.where(UserModel.is_active == is_active)

        stmt = stmt.offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        user_models = result.scalars().all()

        return [self._to_entity(model) for model in user_models]

    async def update(self, user: User) -> User:
        """Update an existing user.

        Args:
            user: User entity with updated data

        Returns:
            Updated user

        Raises:
            NotFoundError: If user not found
            DuplicateEmailError: If new email already exists
        """
        stmt = select(UserModel).where(UserModel.id == user.id)
        result = await self.session.execute(stmt)
        user_model = result.scalar_one_or_none()

        if user_model is None:
            raise NotFoundError("User", str(user.id))

        # Check for duplicate email if email changed
        if user_model.email != user.email:
            if await self.exists_by_email(user.email):
                raise DuplicateEmailError(user.email)

        # Update model fields
        user_model.email = user.email
        user_model.password_hash = user.password_hash
        user_model.full_name = user.name or ""
        user_model.role = user.role.value
        user_model.brand_id = user.brand_id
        user_model.is_active = user.is_active

        await self.session.flush()
        await self.session.refresh(user_model)

        return self._to_entity(user_model)

    async def delete(self, user_id: UUID) -> bool:
        """Delete a user by ID.

        Args:
            user_id: User UUID

        Returns:
            True if deleted, False if not found
        """
        stmt = select(UserModel).where(UserModel.id == user_id)
        result = await self.session.execute(stmt)
        user_model = result.scalar_one_or_none()

        if user_model is None:
            return False

        await self.session.delete(user_model)
        await self.session.flush()

        return True

    async def exists_by_email(self, email: str) -> bool:
        """Check if a user with given email exists.

        Args:
            email: Email address to check

        Returns:
            True if exists, False otherwise
        """
        email = email.strip().lower()
        stmt = select(UserModel.id).where(UserModel.email == email)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def count_by_brand(
        self,
        brand_id: UUID,
        role: UserRole | None = None,
    ) -> int:
        """Count users in a brand.

        Args:
            brand_id: Brand UUID to count users for
            role: Optional role filter

        Returns:
            Number of users
        """
        stmt = select(func.count(UserModel.id)).where(UserModel.brand_id == brand_id)

        if role:
            stmt = stmt.where(UserModel.role == role.value)

        result = await self.session.execute(stmt)
        return result.scalar_one()

    def _to_entity(self, model: UserModel) -> User:
        """Convert UserModel to User entity.

        Args:
            model: UserModel instance

        Returns:
            User entity
        """
        return User(
            id=model.id,
            email=model.email,
            password_hash=model.password_hash,
            role=UserRole(model.role),
            brand_id=model.brand_id,
            name=model.full_name if model.full_name else None,
            is_active=model.is_active,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
