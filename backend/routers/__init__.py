"""
API Routers Package

Contains all API route handlers organized by feature.
"""

from routers.auth import router as auth_router

__all__ = ["auth_router"]

