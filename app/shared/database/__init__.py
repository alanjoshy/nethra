"""
Shared database configuration and base classes.
"""
# IMPORTANT: load all model mappers
from app.core.base import Base
from app.shared.database import models  # noqa: F401
from app.core.database import engine, AsyncSessionLocal, async_session
from app.core.config import settings

__all__ = [
    "Base",
    "engine",
    "AsyncSessionLocal",
    "async_session",
    "settings",
]
