"""
Media Module - Public API

This is the ONLY file that other modules should import from.
All internal implementation details are hidden.
"""

from app.modules.media.entities.media_entity import Media
from app.modules.media.repositories.media_repository import MediaRepository
from app.modules.media.services.media_service import MediaService

__all__ = [
    "Media",
    "MediaRepository",
    "MediaService",
]
