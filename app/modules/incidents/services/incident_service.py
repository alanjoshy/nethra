"""
Incident service - Business logic for incident management.
"""

from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.incidents.entities.incident_entity import Incident
from app.modules.incidents.repositories.incident_repository import IncidentRepository
from app.shared.exceptions import NotFoundError


class IncidentService:
    """
    Incident service.
    Handles business logic for incident operations.
    """
    
    def __init__(self, incident_repository: IncidentRepository):
        self._incident_repository = incident_repository
    
    async def get_incident_by_id(
        self,
        db: AsyncSession,
        incident_id: UUID
    ) -> Incident:
        """
        Get an incident by ID.
        
        Args:
            db: Database session
            incident_id: Incident UUID
        
        Returns:
            Incident object
        
        Raises:
            NotFoundError: If incident not found
        """
        incident = await self._incident_repository.get_incident_by_id(db, incident_id)
        if not incident:
            raise NotFoundError(resource="Incident", identifier=incident_id)
        return incident
