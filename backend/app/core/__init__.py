"""
Core application configuration module.

Contains:
- lifespan: Application startup/shutdown management
- middleware: Middleware registration
- routes: API route registration
"""

from app.core.lifespan import lifespan, validate_middleware_order
from app.core.middleware import register_middleware
from app.core.routes import register_routes

__all__ = [
    "lifespan",
    "validate_middleware_order",
    "register_middleware",
    "register_routes",
]
