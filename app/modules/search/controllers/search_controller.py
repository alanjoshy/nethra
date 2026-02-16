"""
Search controller - unified advanced search endpoint.
"""

from typing import Optional
from datetime import date
from uuid import UUID
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db, require_analyst
from app.modules.users.entities.user_entity import User
from app.modules.search.schemas import SearchResponse
from app.modules.search.services import SearchService


router = APIRouter(
    prefix="/search",
    tags=["Search"],
)


@router.get(
    "",
    response_model=SearchResponse,
    status_code=status.HTTP_200_OK,
    summary="Unified advanced search",
    description="Multi-filter case search with performance-optimized query strategy"
)
async def unified_search(
    radius_km: Optional[float] = Query(None, description="Geographic radius in km", gt=0),
    lat: Optional[float] = Query(None, description="Latitude (required with radius_km)"),
    lng: Optional[float] = Query(None, description="Longitude (required with radius_km)"),
    tags: Optional[str] = Query(None, description="Comma-separated tag filters"),
    from_date: Optional[date] = Query(None, description="Start date filter"),
    to_date: Optional[date] = Query(None, description="End date filter"),
    suspect_name: Optional[str] = Query(None, description="Partial suspect name match"),
    status: Optional[str] = Query(None, description="Case status filter"),
    assigned_officer: Optional[UUID] = Query(None, description="Assigned officer UUID"),
    limit: int = Query(20, description="Maximum results", gt=0, le=100),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_analyst),
):
    """
    Unified case search with multiple filter options.
    
    **Performance-First Filtering Strategy**:
    1. Bounding box/radius filter
    2. Date range filter
    3. Status filter
    4. Tag join
    5. Suspect name partial match
    6. Officer filter
    7. Pagination
    
    **Note**: If using radius_km, both lat and lng are required.
    
    Returns matching cases with incident details.
    """
    # Validate radius requires lat/lng
    if radius_km and (lat is None or lng is None):
        from fastapi import HTTPException
        raise HTTPException(
            status_code=400,
            detail="lat and lng are required when using radius_km"
        )
    
    tag_list = tags.split(",") if tags else None
    
    return await SearchService.unified_search(
        db=db,
        radius_km=radius_km,
        lat=lat,
        lng=lng,
        tags=tag_list,
        from_date=from_date,
        to_date=to_date,
        suspect_name=suspect_name,
        status=status,
        assigned_officer=assigned_officer,
        limit=limit,
    )
