"""API v1 routes package.

All API route modules will be imported here and included in the main app.
"""
from . import brands, menus

# Future router modules will be imported here as they are created
# from . import orders, auth, analytics, ai

__all__ = [
    "brands",
    "menus",
    # "orders",
    # "auth",
    # "analytics",
    # "ai",
]
