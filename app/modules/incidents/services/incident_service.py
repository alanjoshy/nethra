"""
Incident service - Business logic for incident management.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from geoalchemy2.elements import WKTElement

from app.modules.incidents.entities.incident_entity import Incident
from app.modules.incidents.repositories.incident_repository import IncidentRepository
from app.shared.exceptions import NotFoundError


class IncidentService:
    """
    Incident service.
    Handles business logic for incident operations.
    """
    
    @staticmethod
    def _create_point_wkt(longitude: float, latitude: float) -> str:
        """Create WKT POINT string from coordinates."""
        return f"POINT({longitude} {latitude})"
    
    @staticmethod
    async def create_incident(
        db: AsyncSession,
        reported_by: UUID,
        incident_type: str,
        occurred_at: datetime,
        longitude: float,
        latitude: float,
        description: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> Incident:
        """Create a new incident."""
        incident = Incident(
            reported_by=reported_by,
            incident_type=incident_type,
            description=description,
            occurred_at=occurred_at,
            location=IncidentService._create_point_wkt(longitude, latitude),
            notes=notes,
        )
        return await IncidentRepository.create(db, incident)
    
    @staticmethod
    async def list_incidents(db: AsyncSession) -> list[Incident]:
        """Get all incidents."""
        return await IncidentRepository.get_all(db)
    
    @staticmethod
    async def get_incident(db: AsyncSession, incident_id: UUID) -> Incident:
        """Get an incident by ID."""
        incident = await IncidentRepository.get_by_id(db, incident_id)
        if not incident:
            raise NotFoundError(resource="Incident", identifier=incident_id)
        return incident
    
    @staticmethod
    async def update_incident(
        db: AsyncSession,
        incident_id: UUID,
        incident_type: Optional[str] = None,
        description: Optional[str] = None,
        occurred_at: Optional[datetime] = None,
        longitude: Optional[float] = None,
        latitude: Optional[float] = None,
        notes: Optional[str] = None,
    ) -> Incident:
        """Update an incident."""
        incident = await IncidentService.get_incident(db, incident_id)
        
        if incident_type is not None:
            incident.incident_type = incident_type
        if description is not None:
            incident.description = description
        if occurred_at is not None:
            incident.occurred_at = occurred_at
        if longitude is not None and latitude is not None:
            incident.location = IncidentService._create_point_wkt(longitude, latitude)
        if notes is not None:
            incident.notes = notes
        
        return await IncidentRepository.save(db, incident)
    
    @staticmethod
    async def delete_incident(db: AsyncSession, incident_id: UUID) -> None:
        """Delete an incident."""
        incident = await IncidentService.get_incident(db, incident_id)
        await IncidentRepository.delete(db, incident)
