"""Database initialization script.

This script initializes the database by running Alembic migrations.
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path to import from src
sys.path.insert(0, str(Path(__file__).parent.parent))

from alembic import command
from alembic.config import Config

from src.infrastructure.config import settings


def run_migrations():
    """Run Alembic migrations to create database schema."""
    print("🔧 Initializing database...")
    print(f"   Database URL: {settings.DATABASE_URL}")

    # Create Alembic configuration
    alembic_cfg = Config("alembic.ini")

    # Run migrations
    try:
        print("   Running migrations...")
        command.upgrade(alembic_cfg, "head")
        print("✅ Database initialized successfully!")
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        sys.exit(1)


async def create_sample_data():
    """Create sample data for development (optional).

    This function can be used to populate the database with
    sample data for testing and development.
    """
    from sqlalchemy import select

    from src.infrastructure.auth.password_hasher import PasswordHasher
    from src.infrastructure.database.models import BrandModel, UserModel
    from src.infrastructure.database.session import get_session_context

    print("\n🌱 Creating sample data...")

    async with get_session_context() as session:
        # Check if data already exists
        result = await session.execute(select(BrandModel))
        if result.scalar_one_or_none():
            print("   Sample data already exists, skipping...")
            return

        # Create sample brand
        brand = BrandModel(
            name="貓咪食堂",
            slug="cat-canteen",
            description="溫馨的貓咪主題餐廳",
            theme_config={
                "primaryColor": "#FF6B6B",
                "secondaryColor": "#4ECDC4",
                "fontFamily": "Noto Sans TC",
            },
            is_active=True,
        )
        session.add(brand)
        await session.flush()  # Get brand.id

        # Create super admin user
        super_admin = UserModel(
            email="admin@catcanteen.app",
            password_hash=PasswordHasher.hash_password("admin123"),
            full_name="系統管理員",
            role="super_admin",
            is_active=True,
        )
        session.add(super_admin)

        # Create brand admin user
        brand_admin = UserModel(
            email="brand@catcanteen.app",
            password_hash=PasswordHasher.hash_password("brand123"),
            full_name="品牌管理員",
            role="admin",
            brand_id=brand.id,
            is_active=True,
        )
        session.add(brand_admin)

        await session.commit()

        print("✅ Sample data created successfully!")
        print("\n📝 Sample Credentials:")
        print("   Super Admin:")
        print("     Email: admin@catcanteen.app")
        print("     Password: admin123")
        print("\n   Brand Admin:")
        print("     Email: brand@catcanteen.app")
        print("     Password: brand123")


def main():
    """Main function to initialize database."""
    # Run migrations
    run_migrations()

    # Ask if user wants to create sample data
    if settings.is_development:
        response = input("\n❓ Create sample data? (y/N): ").lower()
        if response == "y":
            asyncio.run(create_sample_data())
    else:
        print("\n⚠️  Skipping sample data creation (not in development mode)")


if __name__ == "__main__":
    main()
