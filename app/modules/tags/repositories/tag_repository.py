"""
Tag repository - Data access layer.
"""

from typing import Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.tags.entities.tag_entity import Tag, IncidentTag


class TagRepository:
    """
    Repository for Tag entity.
    Handles all database operations for tags.
    """
    
    @staticmethod
    async def create(
        db: AsyncSession,
        tag: Tag
    ) -> Tag:
        """Create a new tag."""
        db.add(tag)
        await db.commit()
        await db.refresh(tag)
        return tag
    
    @staticmethod
    async def get_by_name(
        db: AsyncSession,
        name: str
    ) -> Optional[Tag]:
        """Get a tag by name."""
        result = await db.execute(
            select(Tag).where(Tag.name == name)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_id(
        db: AsyncSession,
        tag_id: UUID
    ) -> Optional[Tag]:
        """Get a tag by ID."""
        result = await db.execute(
            select(Tag).where(Tag.id == tag_id)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_all(db: AsyncSession) -> list[Tag]:
        """Get all tags."""
        result = await db.execute(select(Tag))
        return list(result.scalars().all())
    
    @staticmethod
    async def link_to_incident(
        db: AsyncSession,
        incident_tag: IncidentTag
    ) -> IncidentTag:
        """Link a tag to an incident."""
        db.add(incident_tag)
        await db.commit()
        await db.refresh(incident_tag)
        return incident_tag

    @staticmethod
    async def get_incident_tag(
        db: AsyncSession,
        incident_id: UUID,
        tag_id: UUID
    ) -> Optional[IncidentTag]:
        """Get an incident-tag link."""
        result = await db.execute(
            select(IncidentTag).where(
                IncidentTag.incident_id == incident_id,
                IncidentTag.tag_id == tag_id
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_tags_by_incident(
        db: AsyncSession,
        incident_id: UUID
    ) -> list[IncidentTag]:
        """Get all tags linked to an incident."""
        result = await db.execute(
            select(IncidentTag)
            .where(IncidentTag.incident_id == incident_id)
            .options(selectinload(IncidentTag.tag))
        )
        return list(result.scalars().all())

    @staticmethod
    async def remove_link(
        db: AsyncSession,
        incident_tag: IncidentTag
    ) -> None:
        """Remove a link between a tag and an incident."""
        await db.delete(incident_tag)
        await db.commit()
