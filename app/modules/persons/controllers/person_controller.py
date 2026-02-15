"""
Person controller - HTTP endpoints for person management.
"""

from uuid import UUID
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db, get_current_user
from app.core.permissions import require_admin
from app.modules.users.entities.user_entity import User
from app.modules.persons.schemas import (
    PersonCreateRequest,
    PersonUpdateRequest,
    PersonResponse,
)
from app.modules.persons.services.person_service import PersonService


router = APIRouter(
    prefix="/persons",
    tags=["Persons"],
)


@router.post("", response_model=PersonResponse, status_code=status.HTTP_201_CREATED)
async def create_person(
    payload: PersonCreateRequest,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """Create a new person."""
    person = await PersonService.create_person(
        db=db,
        name=payload.name,
        date_of_birth=payload.date_of_birth,
        phone=payload.phone,
        address=payload.address,
        identification_number=payload.identification_number,
    )
    return person


@router.get("", response_model=list[PersonResponse], status_code=status.HTTP_200_OK)
async def list_persons(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """List all persons."""
    return await PersonService.list_persons(db)


@router.get("/{person_id}", response_model=PersonResponse, status_code=status.HTTP_200_OK)
async def get_person(
    person_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """Get a specific person by ID."""
    return await PersonService.get_person(db, person_id)


@router.put("/{person_id}", response_model=PersonResponse, status_code=status.HTTP_200_OK)
async def update_person(
    person_id: UUID,
    payload: PersonUpdateRequest,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """Update a person."""
    return await PersonService.update_person(
        db=db,
        person_id=person_id,
        name=payload.name,
        date_of_birth=payload.date_of_birth,
        phone=payload.phone,
        address=payload.address,
        identification_number=payload.identification_number,
    )


@router.delete("/{person_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_person(
    person_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    """Delete a person (admin only)."""
    await PersonService.delete_person(db, person_id)
