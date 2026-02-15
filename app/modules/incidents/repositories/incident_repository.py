"""
Incident repository - Data access layer.
"""

from typing import Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.incidents.entities.incident_entity import Incident


class IncidentRepository:
    """
    Repository for Incident entity.
    Handles all database operations for incidents.
    """
    
    @staticmethod
    async def create(
        db: AsyncSession,
        incident: Incident
    ) -> Incident:
        """Create a new incident."""
        db.add(incident)
        await db.commit()
        await db.refresh(incident)
        return incident
    
    @staticmethod
    async def get_by_id(
        db: AsyncSession,
        incident_id: UUID
    ) -> Optional[Incident]:
        """Get an incident by ID."""
        result = await db.execute(
            select(Incident).where(Incident.id == incident_id)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_all(db: AsyncSession) -> list[Incident]:
        """Get all incidents."""
        result = await db.execute(select(Incident))
        return list(result.scalars().all())
    
    @staticmethod
    async def save(db: AsyncSession, incident: Incident) -> Incident:
        """Update an existing incident."""
        await db.commit()
        await db.refresh(incident)
        return incident
    
    @staticmethod
    async def delete(db: AsyncSession, incident: Incident) -> None:
        """Delete an incident."""
        await db.delete(incident)
        await db.commit()
