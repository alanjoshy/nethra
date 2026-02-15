"""
Media controller - HTTP endpoints for media management.
"""

from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db, get_current_user
from app.core.permissions import require_admin
from app.modules.users.entities.user_entity import User
from app.modules.media.schemas import (
    MediaCreateRequest,
    MediaResponse,
)
from app.modules.media.services.media_service import MediaService


router = APIRouter(
    prefix="/media",
    tags=["Media"],
)


@router.post("", response_model=MediaResponse, status_code=status.HTTP_201_CREATED)
async def create_media(
    payload: MediaCreateRequest,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """Upload/register new media."""
    media = await MediaService.create_media(
        db=db,
        case_id=payload.case_id,
        file_path=payload.file_path,
        media_type=payload.media_type,
        camera_type=payload.camera_type,
        capture_time=payload.capture_time,
    )
    return media


@router.get("", response_model=list[MediaResponse], status_code=status.HTTP_200_OK)
async def list_media(
    case_id: Optional[UUID] = Query(None, description="Filter by case ID"),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """List all media, optionally filtered by case_id."""
    return await MediaService.list_media(db, case_id=case_id)


@router.get("/{media_id}", response_model=MediaResponse, status_code=status.HTTP_200_OK)
async def get_media(
    media_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """Get a specific media by ID."""
    return await MediaService.get_media(db, media_id)


@router.delete("/{media_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_media(
    media_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    """Delete a media record (admin only)."""
    await MediaService.delete_media(db, media_id)
