"""
Media service - Business logic for media management.
"""

from datetime import datetime
from typing import Optional
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
    
    @staticmethod
    async def create_media(
        db: AsyncSession,
        case_id: UUID,
        file_path: str,
        media_type: str,
        camera_type: Optional[str] = None,
        capture_time: Optional[datetime] = None,
    ) -> Media:
        """Create a new media record."""
        media = Media(
            case_id=case_id,
            file_path=file_path,
            media_type=media_type,
            camera_type=camera_type,
            capture_time=capture_time,
        )
        return await MediaRepository.create(db, media)
    
    @staticmethod
    async def list_media(
        db: AsyncSession,
        case_id: Optional[UUID] = None
    ) -> list[Media]:
        """Get all media, optionally filtered by case_id."""
        if case_id:
            return await MediaRepository.get_by_case_id(db, case_id)
        return await MediaRepository.get_all(db)
    
    @staticmethod
    async def get_media(db: AsyncSession, media_id: UUID) -> Media:
        """Get media by ID."""
        media = await MediaRepository.get_by_id(db, media_id)
        if not media:
            raise NotFoundError(resource="Media", identifier=media_id)
        return media
    
    @staticmethod
    async def delete_media(db: AsyncSession, media_id: UUID) -> None:
        """Delete a media record."""
        media = await MediaService.get_media(db, media_id)
        await MediaRepository.delete(db, media)
