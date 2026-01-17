"""
Authentication Module - Public API

This is the ONLY file that other modules should import from.
All internal implementation details are hidden.
"""

from app.modules.auth.controllers.auth_controller import router as auth_router
from app.modules.auth.services.auth_service import AuthService

__all__ = [
    "auth_router",
    "AuthService",
]
