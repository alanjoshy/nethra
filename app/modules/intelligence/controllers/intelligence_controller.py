"""
Intelligence controller - HTTP endpoints for Phase 1 intelligence analysis.
"""

from typing import Optional, List
from uuid import UUID
from datetime import date
from fastapi import APIRouter, Depends, status, Query, Path
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db, require_analyst, require_admin
from app.modules.users.entities.user_entity import User
from app.modules.intelligence.schemas import (
    RelatedCasesResponse,
    RepeatOffendersResponse,
    PatternCorrelationResponse,
    BehaviorSimilarityResponse,
    RiskScoreResponse,
)
from app.modules.intelligence.services.intelligence_service import IntelligenceService


router = APIRouter(
    prefix="/intelligence",
    tags=["Intelligence"],
)

# Separate router for behavior endpoints
behavior_router = APIRouter(
    prefix="/behavior",
    tags=["Behavioral Analysis"],
)

# Separate router for risk endpoints
risk_router = APIRouter(
    prefix="/risk",
    tags=["Risk Scoring"],
)


# ============================================================================
# Intelligence Endpoints
# ============================================================================

@router.get(
    "/related-cases",
    response_model=RelatedCasesResponse,
    status_code=status.HTTP_200_OK,
    summary="Find related cases",
    description="Find cases related to a reference case using multi-dimensional scoring"
)
async def find_related_cases(
    case_id: UUID = Query(..., description="Reference case ID"),
    radius_km: float = Query(5.0, description="Search radius in kilometers", gt=0),
    days_range: int = Query(90, description="Time range in days", gt=0),
    limit: int = Query(10, description="Maximum number of results", gt=0, le=50),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_analyst),
):
    """
    Find cases related to a reference case based on:
    - Tag overlap (weight: 3)
    - Suspect overlap (weight: 4)
    - Geographic proximity (weight: 2)
    - Time similarity (weight: 1)
    
    Returns cases sorted by composite score.
    """
    return await IntelligenceService.find_related_cases(
        db=db,
        case_id=case_id,
        radius_km=radius_km,
        days_range=days_range,
        limit=limit,
    )


@router.get(
    "/repeat-offenders",
    response_model=RepeatOffendersResponse,
    status_code=status.HTTP_200_OK,
    summary="Detect repeat offenders",
    description="Find persons involved in multiple cases with pattern matching"
)
async def find_repeat_offenders(
    tags: Optional[str] = Query(None, description="Comma-separated tag filters"),
    radius_km: Optional[float] = Query(None, description="Geographic radius filter", gt=0),
    from_date: Optional[date] = Query(None, description="Start date filter"),
    to_date: Optional[date] = Query(None, description="End date filter"),
    min_cases: int = Query(2, description="Minimum number of cases", ge=2),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_analyst),
):
    """
    Identify suspects involved in multiple cases.
    
    Filters:
    - Tags: Only include cases with specified tags
    - Date range: Filter by incident dates
    - Min cases: Minimum case count threshold
    
    Returns persons sorted by case count.
    """
    tag_list = tags.split(",") if tags else None
    
    return await IntelligenceService.find_repeat_offenders(
        db=db,
        tags=tag_list,
        radius_km=radius_km,
        from_date=from_date,
        to_date=to_date,
        min_cases=min_cases,
    )


@router.get(
    "/pattern-correlation",
    response_model=PatternCorrelationResponse,
    status_code=status.HTTP_200_OK,
    summary="Analyze pattern correlations",
    description="Find tag co-occurrence patterns and suspect-to-pattern mappings"
)
async def analyze_pattern_correlation(
    case_id: Optional[UUID] = Query(None, description="Optional reference case for filtering"),
    min_occurrence: int = Query(2, description="Minimum occurrence threshold", ge=2),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_analyst),
):
    """
    Analyze correlations between:
    - Tag combinations (which tags occur together)
    - Suspects and their pattern frequencies
    
    Returns tag correlations and suspect pattern scores.
    """
    return await IntelligenceService.analyze_pattern_correlation(
        db=db,
        case_id=case_id,
        min_occurrence=min_occurrence,
    )


# ============================================================================
# Behavioral Analysis Endpoints
# ============================================================================

@behavior_router.get(
    "/similar-cases/{case_id}",
    response_model=BehaviorSimilarityResponse,
    status_code=status.HTTP_200_OK,
    summary="Find behaviorally similar cases",
    description="Find cases with similar behavioral patterns (time, tags, modus operandi)"
)
async def find_similar_cases_behavioral(
    case_id: UUID = Path(..., description="Reference case ID"),
    limit: int = Query(10, description="Maximum number of results", gt=0, le=50),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_analyst),
):
    """
    Find cases with similar behavioral patterns:
    - Time-of-day similarity
    - Weekday vs weekend patterns
    - Tag combination similarity
    
    Returns cases sorted by behavior score.
    """
    return await IntelligenceService.find_similar_cases_behavioral(
        db=db,
        case_id=case_id,
        limit=limit,
    )


# ============================================================================
# Risk Scoring Endpoints
# ============================================================================

@risk_router.get(
    "/person/{person_id}",
    response_model=RiskScoreResponse,
    status_code=status.HTTP_200_OK,
    summary="Calculate person risk score",
    description="Calculate dynamic risk score for a suspect with detailed breakdown"
)
async def calculate_person_risk_score(
    person_id: UUID = Path(..., description="Person ID"),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),  # Admin only
):
    """
    Calculate risk score for a person based on:
    - Repeat offense count (weight: 3)
    - Violent tag frequency (weight: 4)
    - Pattern consistency (weight: 2)
    - Proximity to active cases (weight: 2)
    
    Returns risk score, level (LOW/MEDIUM/HIGH), and detailed breakdown.
    
    **Admin only** - This endpoint requires admin role.
    """
    return await IntelligenceService.calculate_person_risk_score(
        db=db,
        person_id=person_id,
    )
