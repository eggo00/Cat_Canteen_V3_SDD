"""API v1 routes package.

All API route modules will be imported here and included in the main app.
"""
from . import analytics, brands, menus, orders

# Future router modules will be imported here as they are created
# from . import auth, ai

__all__ = [
    "analytics",
    "brands",
    "menus",
    "orders",
    # "auth",
    # "ai",
]
