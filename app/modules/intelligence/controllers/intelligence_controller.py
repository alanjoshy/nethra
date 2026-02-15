"""
Intelligence controller - HTTP endpoints for intelligence gathering.
"""

from typing import Optional
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db, get_current_user
from app.modules.users.entities.user_entity import User
from app.modules.intelligence.schemas import IntelligenceResponse
from app.modules.intelligence.services.intelligence_service import IntelligenceService


router = APIRouter(
    prefix="/intelligence",
    tags=["Intelligence"],
)


@router.get("/related-cases", response_model=IntelligenceResponse, status_code=status.HTTP_200_OK)
async def find_related_cases(
    lat: float = Query(..., description="Latitude", ge=-90, le=90),
    lon: float = Query(..., description="Longitude", ge=-180, le=180),
    radius: float = Query(..., description="Radius in meters", gt=0),
    tags: Optional[str] = Query(None, description="Comma-separated list of tags to filter by"),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """
    Search for related cases based on location and optional tags.
    Returns matching cases and associated suspects with scoring.
    """
    tag_list = tags.split(",") if tags else None
    
    return await IntelligenceService.find_related_cases(
        db=db,
        lat=lat,
        lon=lon,
        radius_meters=radius,
        tags=tag_list,
    )
