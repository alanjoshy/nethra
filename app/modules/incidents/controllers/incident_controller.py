"""
Incident controller - HTTP endpoints for incident management.
"""

from uuid import UUID
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db, get_current_user
from app.core.permissions import require_admin
from app.modules.users.entities.user_entity import User
from app.modules.incidents.schemas import (
    IncidentCreateRequest,
    IncidentUpdateRequest,
    IncidentResponse,
)
from app.modules.incidents.services.incident_service import IncidentService


router = APIRouter(
    prefix="/incidents",
    tags=["Incidents"],
)


@router.post("", response_model=IncidentResponse, status_code=status.HTTP_201_CREATED)
async def create_incident(
    payload: IncidentCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new incident."""
    incident = await IncidentService.create_incident(
        db=db,
        reported_by=current_user.id,
        incident_type=payload.incident_type,
        description=payload.description,
        occurred_at=payload.occurred_at,
        longitude=payload.longitude,
        latitude=payload.latitude,
        notes=payload.notes,
    )
    return incident


@router.get("", response_model=list[IncidentResponse], status_code=status.HTTP_200_OK)
async def list_incidents(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """List all incidents."""
    return await IncidentService.list_incidents(db)


@router.get("/{incident_id}", response_model=IncidentResponse, status_code=status.HTTP_200_OK)
async def get_incident(
    incident_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """Get a specific incident by ID."""
    return await IncidentService.get_incident(db, incident_id)


@router.put("/{incident_id}", response_model=IncidentResponse, status_code=status.HTTP_200_OK)
async def update_incident(
    incident_id: UUID,
    payload: IncidentUpdateRequest,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """Update an incident."""
    return await IncidentService.update_incident(
        db=db,
        incident_id=incident_id,
        incident_type=payload.incident_type,
        description=payload.description,
        occurred_at=payload.occurred_at,
        longitude=payload.longitude,
        latitude=payload.latitude,
        notes=payload.notes,
    )


@router.delete("/{incident_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_incident(
    incident_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    """Delete an incident (admin only)."""
    await IncidentService.delete_incident(db, incident_id)
