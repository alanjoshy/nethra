"""
Geospatial controller - heatmap and cluster detection endpoints.
"""

from typing import Optional, List
from datetime import date
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db, require_analyst
from app.modules.users.entities.user_entity import User
from app.modules.geo.schemas import (
    HeatmapResponse,
    ClustersResponse,
)
from app.modules.geo.services import GeoService


router = APIRouter(
    prefix="/geo",
    tags=["Geospatial"],
)


@router.get(
    "/heatmap",
    response_model=HeatmapResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate crime heatmap",
    description="Generate crime density heatmap within geographic boundary using grid-based spatial aggregation"
)
async def get_crime_heatmap(
    min_lat: float = Query(..., description="Bounding box minimum latitude"),
    min_lng: float = Query(..., description="Bounding box minimum longitude"),
    max_lat: float = Query(..., description="Bounding box maximum latitude"),
    max_lng: float = Query(..., description="Bounding box maximum longitude"),
    from_date: Optional[date] = Query(None, description="Start date filter"),
    to_date: Optional[date] = Query(None, description="End date filter"),
    tags: Optional[str] = Query(None, description="Comma-separated tag filters"),
    grid_size_meters: int = Query(250, description="Grid cell size in meters", gt=0, le=1000),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_analyst),
):
    """
    Generate crime density heatmap using spatial grid aggregation.
    
    **Features**:
    - PostGIS ST_MakeEnvelope for bounding box filtering  
    - Grid-based spatial bucketing  
    - Density level classification (LOW, MEDIUM, HIGH)  
    - Optional date and tag filters  
    
    Returns grid cells with incident counts and density levels.
    """
    tag_list = tags.split(",") if tags else None
    
    return await GeoService.generate_heatmap(
        db=db,
        min_lat=min_lat,
        min_lng=min_lng,
        max_lat=max_lat,
        max_lng=max_lng,
        from_date=from_date,
        to_date=to_date,
        tags=tag_list,
        grid_size_meters=grid_size_meters,
    )


@router.get(
    "/clusters",
    response_model=ClustersResponse,
    status_code=status.HTTP_200_OK,
    summary="Detect crime clusters",
    description="Detect spatial crime clusters using density-based algorithm"
)
async def detect_crime_clusters(
    radius_meters: int = Query(500, description="Clustering radius in meters", gt=0),
    min_points: int = Query(3, description="Minimum points to form cluster", ge=2),
    from_date: Optional[date] = Query(None, description="Start date filter"),
    tags: Optional[str] = Query(None, description="Comma-separated tag filters"),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_analyst),
):
    """
    Detect spatial crime clusters using density-based grouping.
    
    **Algorithm**:
    - Groups incidents within radius_meters of each other  
    - Requires min_points to form a cluster  
    - Calculates cluster centroids  
    
    Returns detected clusters with metadata.
    """
    tag_list = tags.split(",") if tags else None
    
    return await GeoService.detect_clusters(
        db=db,
        radius_meters=radius_meters,
        min_points=min_points,
        from_date=from_date,
        tags=tag_list,
    )
