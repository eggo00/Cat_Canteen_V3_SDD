"""Seed script to create initial admin user and demo data."""
import asyncio
import os
import sys
from uuid import uuid4

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from src.infrastructure.database.session import async_engine, AsyncSessionLocal
from src.infrastructure.auth.password_hasher import PasswordHasher


async def seed_database():
    """Create initial admin user and demo brand with menu."""

    async with async_engine.begin() as conn:
        # Create tables if they don't exist
        print("Creating tables...")
        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS users (
                id UUID PRIMARY KEY,
                email VARCHAR(255) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                full_name VARCHAR(255),
                role VARCHAR(50) NOT NULL DEFAULT 'customer',
                brand_id UUID,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))

        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS brands (
                id UUID PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                slug VARCHAR(255) UNIQUE NOT NULL,
                description TEXT,
                logo_url VARCHAR(500),
                primary_color VARCHAR(7) DEFAULT '#FF6B6B',
                secondary_color VARCHAR(7) DEFAULT '#4ECDC4',
                accent_color VARCHAR(7) DEFAULT '#FFE66D',
                background_color VARCHAR(7) DEFAULT '#FFFFFF',
                text_color VARCHAR(7) DEFAULT '#2C3E50',
                font_family VARCHAR(100) DEFAULT 'Inter, system-ui, sans-serif',
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))

        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS categories (
                id UUID PRIMARY KEY,
                brand_id UUID NOT NULL REFERENCES brands(id),
                name VARCHAR(255) NOT NULL,
                description TEXT,
                display_order INTEGER DEFAULT 0,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))

        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS menu_items (
                id UUID PRIMARY KEY,
                category_id UUID NOT NULL REFERENCES categories(id),
                name VARCHAR(255) NOT NULL,
                description TEXT,
                price DECIMAL(10, 2) NOT NULL,
                image_url VARCHAR(500),
                is_available BOOLEAN DEFAULT TRUE,
                is_popular BOOLEAN DEFAULT FALSE,
                display_order INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))

        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS orders (
                id UUID PRIMARY KEY,
                brand_id UUID NOT NULL REFERENCES brands(id),
                order_number VARCHAR(50) UNIQUE NOT NULL,
                customer_name VARCHAR(255),
                customer_phone VARCHAR(50),
                status VARCHAR(50) DEFAULT 'pending',
                subtotal DECIMAL(10, 2) NOT NULL,
                tax DECIMAL(10, 2) DEFAULT 0,
                total DECIMAL(10, 2) NOT NULL,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))

        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS order_items (
                id UUID PRIMARY KEY,
                order_id UUID NOT NULL REFERENCES orders(id),
                menu_item_id UUID NOT NULL REFERENCES menu_items(id),
                quantity INTEGER NOT NULL,
                unit_price DECIMAL(10, 2) NOT NULL,
                subtotal DECIMAL(10, 2) NOT NULL,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))

        print("Tables created.")

    async with AsyncSessionLocal() as session:
        # Check if admin already exists
        result = await session.execute(
            text("SELECT id FROM users WHERE email = 'admin@catcanteen.com'")
        )
        existing_admin = result.fetchone()
        password_hash = PasswordHasher.hash_password("Admin123!")

        if existing_admin:
            # Update existing admin's password (in case it was corrupted)
            await session.execute(
                text("UPDATE users SET password_hash = :password_hash WHERE email = 'admin@catcanteen.com'"),
                {"password_hash": password_hash}
            )
            print("Admin user exists. Password has been reset to: Admin123!")
        else:
            # Create admin user
            admin_id = uuid4()

            await session.execute(
                text("""
                    INSERT INTO users (id, email, password_hash, full_name, role, is_active)
                    VALUES (:id, :email, :password_hash, :name, :role, TRUE)
                """),
                {
                    "id": admin_id,
                    "email": "admin@catcanteen.com",
                    "password_hash": password_hash,
                    "name": "Super Admin",
                    "role": "super_admin",
                }
            )
            print(f"Created admin user: admin@catcanteen.com / Admin123!")

        # Check if demo brand exists
        result = await session.execute(
            text("SELECT id FROM brands WHERE slug = 'demo-cafe'")
        )
        brand_row = result.fetchone()

        if brand_row:
            brand_id = brand_row[0]
            print("Demo brand already exists.")
        else:
            # Create demo brand
            brand_id = uuid4()
            await session.execute(
                text("""
                    INSERT INTO brands (id, name, slug, description, primary_color, secondary_color)
                    VALUES (:id, :name, :slug, :description, :primary_color, :secondary_color)
                """),
                {
                    "id": brand_id,
                    "name": "Demo Cafe",
                    "slug": "demo-cafe",
                    "description": "歡迎來到 Demo Cafe！我們提供各式精選咖啡和輕食。",
                    "primary_color": "#8B4513",
                    "secondary_color": "#D2691E",
                }
            )
            print(f"Created demo brand: demo-cafe")

            # Create categories
            drinks_id = uuid4()
            food_id = uuid4()
            desserts_id = uuid4()

            await session.execute(
                text("""
                    INSERT INTO categories (id, brand_id, name, description, display_order)
                    VALUES
                        (:drinks_id, :brand_id, '飲品', '各式咖啡和茶飲', 1),
                        (:food_id, :brand_id, '輕食', '三明治和沙拉', 2),
                        (:desserts_id, :brand_id, '甜點', '蛋糕和點心', 3)
                """),
                {
                    "drinks_id": drinks_id,
                    "food_id": food_id,
                    "desserts_id": desserts_id,
                    "brand_id": brand_id,
                }
            )
            print("Created categories: 飲品, 輕食, 甜點")

            # Create menu items
            menu_items = [
                # Drinks
                (uuid4(), drinks_id, "美式咖啡", "經典美式，香醇濃郁", 60, True),
                (uuid4(), drinks_id, "拿鐵咖啡", "濃郁咖啡配上綿密奶泡", 80, True),
                (uuid4(), drinks_id, "卡布奇諾", "義式經典，奶泡豐富", 85, False),
                (uuid4(), drinks_id, "抹茶拿鐵", "日式抹茶與牛奶的完美結合", 90, True),
                (uuid4(), drinks_id, "紅茶拿鐵", "錫蘭紅茶配上鮮奶", 75, False),
                # Food
                (uuid4(), food_id, "火腿起司三明治", "經典組合，滿足一整天", 120, True),
                (uuid4(), food_id, "燻鮭魚貝果", "新鮮燻鮭魚配奶油起司", 150, False),
                (uuid4(), food_id, "凱薩沙拉", "羅蔓生菜配帕瑪森起司", 130, False),
                # Desserts
                (uuid4(), desserts_id, "提拉米蘇", "義式經典甜點", 120, True),
                (uuid4(), desserts_id, "紐約起司蛋糕", "濃郁起司香", 110, False),
                (uuid4(), desserts_id, "巧克力布朗尼", "濃厚巧克力風味", 90, True),
            ]

            for item_id, cat_id, name, desc, price, is_popular in menu_items:
                await session.execute(
                    text("""
                        INSERT INTO menu_items (id, category_id, name, description, price, is_popular, is_available)
                        VALUES (:id, :category_id, :name, :description, :price, :is_popular, TRUE)
                    """),
                    {
                        "id": item_id,
                        "category_id": cat_id,
                        "name": name,
                        "description": desc,
                        "price": price,
                        "is_popular": is_popular,
                    }
                )
            print(f"Created {len(menu_items)} menu items")

        await session.commit()
        print("\n✅ Seed data created successfully!")
        print("\n📋 Test credentials:")
        print("   Email: admin@catcanteen.com")
        print("   Password: Admin123!")
        print(f"\n🌐 Demo menu: https://cat-canteen-frontend.zeabur.app/demo-cafe/menu")


if __name__ == "__main__":
    asyncio.run(seed_database())
