"""
Media repository - Data access layer.
"""

from typing import Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.media.entities.media_entity import Media


class MediaRepository:
    """
    Repository for Media entity.
    Handles all database operations for media.
    """
    
    async def get_media_by_id(
        self,
        db: AsyncSession,
        media_id: UUID
    ) -> Optional[Media]:
        """
        Get media by ID.
        
        Args:
            db: Database session
            media_id: Media UUID
        
        Returns:
            Media object if found, None otherwise
        """
        result = await db.execute(
            select(Media).where(Media.id == media_id)
        )
        return result.scalar_one_or_none()
