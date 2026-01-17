"""
Users Module - Public API

This is the ONLY file that other modules should import from.
All internal implementation details are hidden.
"""

from app.modules.users.repositories.user_repository import UserRepository
from app.modules.users.services.user_service import UserService
from app.modules.users.entities.user_entity import User

__all__ = [
    "UserRepository",
    "UserService",
    "User",
]
