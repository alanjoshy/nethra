"""
Media service - Business logic for media management.
"""

from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.media.entities.media_entity import Media
from app.modules.media.repositories.media_repository import MediaRepository
from app.shared.exceptions import NotFoundError


class MediaService:
    """
    Media service.
    Handles business logic for media operations.
    """
    
    def __init__(self, media_repository: MediaRepository):
        self._media_repository = media_repository
    
    async def get_media_by_id(
        self,
        db: AsyncSession,
        media_id: UUID
    ) -> Media:
        """
        Get media by ID.
        
        Args:
            db: Database session
            media_id: Media UUID
        
        Returns:
            Media object
        
        Raises:
            NotFoundError: If media not found
        """
        media = await self._media_repository.get_media_by_id(db, media_id)
        if not media:
            raise NotFoundError(resource="Media", identifier=media_id)
        return media
