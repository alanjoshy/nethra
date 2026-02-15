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
    
    @staticmethod
    async def create(
        db: AsyncSession,
        media: Media
    ) -> Media:
        """Create a new media record."""
        db.add(media)
        await db.commit()
        await db.refresh(media)
        return media
    
    @staticmethod
    async def get_by_id(
        db: AsyncSession,
        media_id: UUID
    ) -> Optional[Media]:
        """Get media by ID."""
        result = await db.execute(
            select(Media).where(Media.id == media_id)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_by_case_id(
        db: AsyncSession,
        case_id: UUID
    ) -> list[Media]:
        """Get all media for a specific case."""
        result = await db.execute(
            select(Media).where(Media.case_id == case_id)
        )
        return list(result.scalars().all())
    
    @staticmethod
    async def get_all(db: AsyncSession) -> list[Media]:
        """Get all media."""
        result = await db.execute(select(Media))
        return list(result.scalars().all())
    
    @staticmethod
    async def delete(db: AsyncSession, media: Media) -> None:
        """Delete a media record."""
        await db.delete(media)
        await db.commit()
