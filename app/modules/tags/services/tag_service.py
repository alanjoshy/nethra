"""
Tag service - Business logic for tag management.
"""

from typing import Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.tags.entities.tag_entity import Tag, IncidentTag
from app.modules.tags.repositories.tag_repository import TagRepository
from app.shared.exceptions import NotFoundError, ValidationError


class TagService:
    """
    Tag service.
    Handles business logic for tag operations.
    """
    
    @staticmethod
    async def create_tag(
        db: AsyncSession,
        name: str,
    ) -> Tag:
        """Create a new tag or return existing."""
        # Check if tag exists
        existing_tag = await TagRepository.get_by_name(db, name)
        if existing_tag:
            return existing_tag

        tag = Tag(name=name)
        return await TagRepository.create(db, tag)
    
    @staticmethod
    async def list_tags(db: AsyncSession) -> list[Tag]:
        """Get all tags."""
        return await TagRepository.get_all(db)
    
    @staticmethod
    async def tag_incident(
        db: AsyncSession,
        incident_id: UUID,
        tag_names: list[str]
    ) -> list[IncidentTag]:
        """Link tags to an incident."""
        links = []
        for name in tag_names:
            # Get or create tag
            tag = await TagService.create_tag(db, name)
            
            # Check if link already exists
            existing_link = await TagRepository.get_incident_tag(db, incident_id, tag.id)
            if not existing_link:
                link = IncidentTag(
                    incident_id=incident_id,
                    tag_id=tag.id
                )
                created_link = await TagRepository.link_to_incident(db, link)
                # Need to refresh/reload to get the tag relationship populated for response
                # But since we just created it, we can return a constructed object or fetch again
                # For simplicity, we'll fetch all tags at the end or just append here
                created_link.tag = tag # Manually set for response
                links.append(created_link)
        
        return await TagRepository.get_tags_by_incident(db, incident_id)

    @staticmethod
    async def get_tags_for_incident(
        db: AsyncSession,
        incident_id: UUID
    ) -> list[IncidentTag]:
        """Get all tags linked to an incident."""
        return await TagRepository.get_tags_by_incident(db, incident_id)

    @staticmethod
    async def remove_tag_from_incident(
        db: AsyncSession,
        incident_id: UUID,
        tag_id: UUID
    ) -> None:
        """Remove a tag from an incident."""
        link = await TagRepository.get_incident_tag(db, incident_id, tag_id)
        if not link:
            raise NotFoundError(resource="IncidentTagLink", identifier=f"{incident_id}-{tag_id}")
        
        await TagRepository.remove_link(db, link)
