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
    
    async def get_incident_by_id(
        self,
        db: AsyncSession,
        incident_id: UUID
    ) -> Optional[Incident]:
        """
        Get an incident by ID.
        
        Args:
            db: Database session
            incident_id: Incident UUID
        
        Returns:
            Incident object if found, None otherwise
        """
        result = await db.execute(
            select(Incident).where(Incident.id == incident_id)
        )
        return result.scalar_one_or_none()
