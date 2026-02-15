"""
Case controller - HTTP endpoints for case management.
"""

from uuid import UUID
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db, get_current_user
from app.core.permissions import require_admin
from app.modules.users.entities.user_entity import User
from app.modules.cases.schemas import (
    CaseCreateRequest,
    CaseUpdateRequest,
    CaseStatusUpdateRequest,
    CaseResponse,
)
from app.modules.cases.services.case_service import CaseService


router = APIRouter(
    prefix="/cases",
    tags=["Cases"],
)


@router.post("", response_model=CaseResponse, status_code=status.HTTP_201_CREATED)
async def create_case(
    payload: CaseCreateRequest,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """Create a new case."""
    case = await CaseService.create_case(
        db=db,
        primary_incident_id=payload.primary_incident_id,
        title=payload.title,
        status=payload.status,
        notes=payload.notes,
    )
    return case


@router.get("", response_model=list[CaseResponse], status_code=status.HTTP_200_OK)
async def list_cases(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """List all cases."""
    return await CaseService.list_cases(db)


@router.get("/{case_id}", response_model=CaseResponse, status_code=status.HTTP_200_OK)
async def get_case(
    case_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """Get a specific case by ID."""
    return await CaseService.get_case(db, case_id)


@router.put("/{case_id}", response_model=CaseResponse, status_code=status.HTTP_200_OK)
async def update_case(
    case_id: UUID,
    payload: CaseUpdateRequest,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """Update a case."""
    return await CaseService.update_case(
        db=db,
        case_id=case_id,
        title=payload.title,
        notes=payload.notes,
    )


@router.patch("/{case_id}/status", response_model=CaseResponse, status_code=status.HTTP_200_OK)
async def update_case_status(
    case_id: UUID,
    payload: CaseStatusUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update case status and record in history."""
    return await CaseService.update_case_status(
        db=db,
        case_id=case_id,
        new_status=payload.new_status,
        changed_by=current_user.id,
    )


@router.delete("/{case_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_case(
    case_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    """Delete a case (admin only)."""
    await CaseService.delete_case(db, case_id)


# Person Linking Endpoints

from app.modules.persons.services.person_service import PersonService
from app.modules.persons.schemas import CasePersonLinkRequest, CasePersonResponse


@router.post("/{case_id}/persons", response_model=CasePersonResponse, status_code=status.HTTP_201_CREATED)
async def link_person_to_case(
    case_id: UUID,
    payload: CasePersonLinkRequest,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """Link a person to a case."""
    return await PersonService.link_person_to_case(
        db=db,
        case_id=case_id,
        person_id=payload.person_id,
        role=payload.role,
    )


@router.get("/{case_id}/persons", response_model=list[CasePersonResponse], status_code=status.HTTP_200_OK)
async def list_case_persons(
    case_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """List all persons linked to a case."""
    return await PersonService.get_persons_for_case(db, case_id)


@router.delete("/{case_id}/persons/{person_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_person_from_case(
    case_id: UUID,
    person_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    """Remove a person from a case (admin only)."""
    await PersonService.remove_person_from_case(db, case_id, person_id)
