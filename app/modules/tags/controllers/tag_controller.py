"""
Tag controller - HTTP endpoints for tag management.
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db, get_current_user
from app.modules.users.entities.user_entity import User
from app.modules.tags.schemas import (
    TagCreateRequest,
    TagResponse,
)
from app.modules.tags.services.tag_service import TagService


router = APIRouter(
    prefix="/tags",
    tags=["Tags"],
)


@router.post("", response_model=TagResponse, status_code=status.HTTP_201_CREATED)
async def create_tag(
    payload: TagCreateRequest,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """Create a new tag."""
    return await TagService.create_tag(db, name=payload.name)


@router.get("", response_model=list[TagResponse], status_code=status.HTTP_200_OK)
async def list_tags(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """List all tags."""
    return await TagService.list_tags(db)
