"""Initial schema with all 7 entities

Revision ID: 001_initial
Revises:
Create Date: 2026-01-08 23:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create brands table
    op.create_table(
        'brands',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('name', sa.String(255), nullable=False, index=True),
        sa.Column('slug', sa.String(255), unique=True, nullable=False, index=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('logo_url', sa.String(2048), nullable=True),
        sa.Column('theme_config', postgresql.JSONB(), nullable=False, server_default='{}'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true', index=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # Create menu_categories table
    op.create_table(
        'menu_categories',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('brand_id', postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column('name', sa.String(255), nullable=False, index=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('display_order', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['brand_id'], ['brands.id'], ondelete='CASCADE'),
    )

    # Create menu_items table
    op.create_table(
        'menu_items',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('category_id', postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column('name', sa.String(255), nullable=False, index=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('price', sa.Numeric(10, 2), nullable=False),
        sa.Column('image_url', sa.String(2048), nullable=True),
        sa.Column('display_order', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('is_available', sa.Boolean(), nullable=False, server_default='true', index=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['category_id'], ['menu_categories.id'], ondelete='CASCADE'),
    )

    # Create customization_options table
    op.create_table(
        'customization_options',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('menu_item_id', postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column('option_type', sa.String(50), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('price_adjustment', sa.Numeric(10, 2), nullable=False, server_default='0'),
        sa.Column('constraints', postgresql.JSONB(), nullable=True),
        sa.Column('display_order', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['menu_item_id'], ['menu_items.id'], ondelete='CASCADE'),
    )

    # Create users table
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('email', sa.String(255), unique=True, nullable=False, index=True),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('full_name', sa.String(255), nullable=False),
        sa.Column('role', sa.String(50), nullable=False, server_default='customer', index=True),
        sa.Column('brand_id', postgresql.UUID(as_uuid=True), nullable=True, index=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true', index=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['brand_id'], ['brands.id'], ondelete='SET NULL'),
    )

    # Create orders table
    op.create_table(
        'orders',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('brand_id', postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column('order_number', sa.String(50), unique=True, nullable=False, index=True),
        sa.Column('customer_name', sa.String(255), nullable=False),
        sa.Column('customer_phone', sa.String(20), nullable=False, index=True),
        sa.Column('customer_email', sa.String(255), nullable=True),
        sa.Column('status', sa.String(50), nullable=False, server_default='pending', index=True),
        sa.Column('total_amount', sa.Numeric(10, 2), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['brand_id'], ['brands.id'], ondelete='CASCADE'),
    )

    # Create order_items table
    op.create_table(
        'order_items',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('order_id', postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column('menu_item_id', postgresql.UUID(as_uuid=True), nullable=True, index=True),
        sa.Column('menu_item_name', sa.String(255), nullable=False),
        sa.Column('unit_price', sa.Numeric(10, 2), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('customizations', postgresql.JSONB(), nullable=True),
        sa.Column('subtotal', sa.Numeric(10, 2), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['order_id'], ['orders.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['menu_item_id'], ['menu_items.id'], ondelete='SET NULL'),
    )

    # Create indexes for performance
    op.create_index('idx_menu_categories_brand_id', 'menu_categories', ['brand_id', 'display_order'])
    op.create_index('idx_menu_items_category_id', 'menu_items', ['category_id', 'display_order'])
    op.create_index('idx_orders_brand_created', 'orders', ['brand_id', 'created_at'])
    op.create_index('idx_orders_status_created', 'orders', ['status', 'created_at'])

    # Create GIN indexes for JSONB columns
    op.create_index('idx_brands_theme_config_gin', 'brands', ['theme_config'], postgresql_using='gin')
    op.create_index('idx_customization_constraints_gin', 'customization_options', ['constraints'], postgresql_using='gin')
    op.create_index('idx_order_items_customizations_gin', 'order_items', ['customizations'], postgresql_using='gin')


def downgrade() -> None:
    # Drop tables in reverse order (respecting foreign keys)
    op.drop_table('order_items')
    op.drop_table('orders')
    op.drop_table('users')
    op.drop_table('customization_options')
    op.drop_table('menu_items')
    op.drop_table('menu_categories')
    op.drop_table('brands')
