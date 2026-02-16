"""
Analytics controller - aggregated reporting endpoints.
"""

from typing import Optional
from datetime import date
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db, require_admin
from app.modules.users.entities.user_entity import User
from app.modules.analytics.schemas import (
    CrimeByLocationResponse,
    PatternFrequencyResponse,
    MonthlyTrendsResponse,
    RepeatOffenderOverviewResponse,
)
from app.modules.analytics.services import AnalyticsService


router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"],
)


@router.get(
    "/crime-by-location",
    response_model=CrimeByLocationResponse,
    status_code=status.HTTP_200_OK,
    summary="Crime by location analytics",
    description="Aggregate incidents by district/region"
)
async def crime_by_location(
    district: Optional[str] = Query(None, description="Optional district filter"),
    from_date: Optional[date] = Query(None, description="Start date filter"),
    to_date: Optional[date] = Query(None, description="End date filter"),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    """
    Aggregate crime statistics by district/location.
    
    Returns district-level incident counts sorted by frequency.
    
    **Admin only**.
    """
    return await AnalyticsService.crime_by_location(
        db=db,
        district=district,
        from_date=from_date,
        to_date=to_date,
    )


@router.get(
    "/pattern-frequency",
    response_model=PatternFrequencyResponse,
    status_code=status.HTTP_200_OK,
    summary="Pattern frequency analytics",
    description="Aggregate tag occurrence statistics"
)
async def pattern_frequency(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    """
    Aggregate tag/pattern occurrence frequencies.
    
    Returns tag statistics sorted by occurrence count (descending).
    
    **Admin only**.
    """
    return await AnalyticsService.pattern_frequency(db=db)


@router.get(
    "/monthly-trends",
    response_model=MonthlyTrendsResponse,
    status_code=status.HTTP_200_OK,
    summary="Monthly crime trends",
    description="Time-series crime distribution by month"
)
async def monthly_trends(
    year: int = Query(..., description="Year to analyze", ge=2000, le=2100),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    """
    Aggregate crime statistics by month for a given year.
    
    Returns monthly incident counts for time-series visualization.
    
    **Admin only**.
    """
    return await AnalyticsService.monthly_trends(db=db, year=year)


@router.get(
    "/repeat-offenders",
    response_model=RepeatOffenderOverviewResponse,
    status_code=status.HTTP_200_OK,
    summary="Repeat offender overview",
    description="Aggregate repeat offenders with case counts"
)
async def repeat_offenders(
    min_cases: int = Query(2, description="Minimum case count threshold", ge=2),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    """
    Aggregate repeat offenders with case involvement counts.
    
    Returns suspects involved in multiple cases sorted by case count.
    
    **Admin only**.
    """
    return await AnalyticsService.repeat_offender_overview(
        db=db,
        min_cases=min_cases,
    )
