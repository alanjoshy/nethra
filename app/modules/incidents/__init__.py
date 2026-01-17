"""
Incidents Module - Public API

This is the ONLY file that other modules should import from.
All internal implementation details are hidden.
"""

from app.modules.incidents.entities.incident_entity import Incident
from app.modules.incidents.repositories.incident_repository import IncidentRepository
from app.modules.incidents.services.incident_service import IncidentService

__all__ = [
    "Incident",
    "IncidentRepository",
    "IncidentService",
]
