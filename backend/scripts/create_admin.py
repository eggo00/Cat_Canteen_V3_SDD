"""Script to create admin users.

Usage:
    python scripts/create_admin.py --email admin@example.com --name "Admin Name" --role admin
"""
import argparse
import asyncio
import sys
from pathlib import Path
from uuid import UUID

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select

from src.infrastructure.auth.password_hasher import PasswordHasher
from src.infrastructure.database.models import BrandModel, UserModel
from src.infrastructure.database.session import get_session_context


async def create_admin(
    email: str,
    full_name: str,
    password: str,
    role: str = "admin",
    brand_id: str | None = None,
):
    """Create an admin user.

    Args:
        email: User email address
        full_name: Full name of the user
        password: Plain text password (will be hashed)
        role: User role (admin or super_admin)
        brand_id: Optional brand ID (required for role='admin')
    """
    async with get_session_context() as session:
        # Check if user already exists
        result = await session.execute(select(UserModel).where(UserModel.email == email))
        existing_user = result.scalar_one_or_none()

        if existing_user:
            print(f"❌ User with email {email} already exists!")
            return

        # Validate brand_id if provided
        brand_uuid = None
        if brand_id:
            try:
                brand_uuid = UUID(brand_id)
                result = await session.execute(
                    select(BrandModel).where(BrandModel.id == brand_uuid)
                )
                brand = result.scalar_one_or_none()
                if not brand:
                    print(f"❌ Brand with ID {brand_id} not found!")
                    return
            except ValueError:
                print(f"❌ Invalid brand ID format: {brand_id}")
                return

        # Create user
        user = UserModel(
            email=email,
            password_hash=PasswordHasher.hash_password(password),
            full_name=full_name,
            role=role,
            brand_id=brand_uuid,
            is_active=True,
        )

        session.add(user)
        await session.commit()

        print(f"✅ Admin user created successfully!")
        print(f"\n   Email: {email}")
        print(f"   Name: {full_name}")
        print(f"   Role: {role}")
        if brand_uuid:
            print(f"   Brand ID: {brand_uuid}")


def main():
    """Parse arguments and create admin user."""
    parser = argparse.ArgumentParser(description="Create an admin user")
    parser.add_argument("--email", required=True, help="User email address")
    parser.add_argument("--name", required=True, help="Full name")
    parser.add_argument(
        "--password",
        help="Password (if not provided, will prompt securely)",
    )
    parser.add_argument(
        "--role",
        choices=["admin", "super_admin"],
        default="admin",
        help="User role (default: admin)",
    )
    parser.add_argument(
        "--brand-id",
        help="Brand ID (required for role=admin, not used for super_admin)",
    )

    args = parser.parse_args()

    # Validate role and brand_id
    if args.role == "admin" and not args.brand_id:
        print("❌ --brand-id is required for role='admin'")
        sys.exit(1)

    if args.role == "super_admin" and args.brand_id:
        print("⚠️  Warning: --brand-id is ignored for super_admin role")
        args.brand_id = None

    # Get password
    if args.password:
        password = args.password
    else:
        import getpass

        password = getpass.getpass("Enter password: ")
        password_confirm = getpass.getpass("Confirm password: ")

        if password != password_confirm:
            print("❌ Passwords do not match!")
            sys.exit(1)

    # Create admin user
    asyncio.run(
        create_admin(
            email=args.email,
            full_name=args.name,
            password=password,
            role=args.role,
            brand_id=args.brand_id,
        )
    )


if __name__ == "__main__":
    main()
