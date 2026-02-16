"""
Intelligence schemas for request/response validation - Phase 1.
"""

from typing import Optional, List
from uuid import UUID
from datetime import datetime, date
from pydantic import BaseModel, Field


# ============================================================================
# Related Cases Intelligence
# ============================================================================

class RelatedCaseResult(BaseModel):
    """Individual related case result with scoring breakdown."""
    
    case_id: str
    score: float = Field(description="Composite score based on multiple factors")
    distance_km: float = Field(description="Geographic distance in kilometers")
    tag_overlap_count: int = Field(description="Number of overlapping tags")
    suspect_overlap_count: int = Field(description="Number of shared suspects")


class RelatedCasesResponse(BaseModel):
    """Response for related cases intelligence query."""
    
    reference_case_id: str
    results: List[RelatedCaseResult]


# ============================================================================
# Repeat Offenders Detection
# ============================================================================

class RepeatOffenderResult(BaseModel):
    """Individual repeat offender result."""
    
    person_id: str
    name: str
    case_count: int = Field(description="Total number of cases person is involved in")
    pattern_match_count: int = Field(description="Number of cases with similar patterns")
    last_seen_date: datetime = Field(description="Most recent incident date")


class RepeatOffendersResponse(BaseModel):
    """Response for repeat offenders detection."""
    
    results: List[RepeatOffenderResult]


# ============================================================================
# Pattern Correlation Engine
# ============================================================================

class TagCorrelation(BaseModel):
    """Tag combination correlation."""
    
    tag_combination: List[str] = Field(description="List of tags that occur together")
    occurrence_count: int = Field(description="Number of times this combination appears")


class SuspectPattern(BaseModel):
    """Suspect to pattern mapping."""
    
    person_id: str
    pattern_score: float = Field(description="Frequency/consistency score for this pattern")


class PatternCorrelationResponse(BaseModel):
    """Response for pattern correlation analysis."""
    
    tag_correlations: List[TagCorrelation]
    suspect_pattern_map: List[SuspectPattern]


# ============================================================================
# Behavioral Similarity Engine
# ============================================================================

class BehaviorSimilarityResult(BaseModel):
    """Individual behavioral similarity result."""
    
    case_id: str
    behavior_score: float = Field(description="Composite behavioral similarity score")
    time_similarity: float = Field(ge=0.0, le=1.0, description="Temporal pattern similarity (0-1)")
    tag_similarity: float = Field(ge=0.0, le=1.0, description="Tag pattern similarity (0-1)")


class BehaviorSimilarityResponse(BaseModel):
    """Response for behavioral similarity query."""
    
    reference_case_id: str
    behavior_similarity_results: List[BehaviorSimilarityResult]


# ============================================================================
# Risk Scoring System
# ============================================================================

class RiskBreakdown(BaseModel):
    """Detailed breakdown of risk score components."""
    
    repeat_offense_count: int = Field(description="Number of repeat offenses")
    violent_tag_frequency: int = Field(description="Count of violent-related tags")
    pattern_consistency: float = Field(ge=0.0, le=1.0, description="Pattern consistency score (0-1)")
    proximity_factor: float = Field(description="Geographic proximity to active cases")


class RiskScoreResponse(BaseModel):
    """Response for person risk scoring."""
    
    person_id: str
    risk_score: float = Field(description="Composite risk score")
    risk_level: str = Field(description="Risk level: LOW, MEDIUM, or HIGH")
    breakdown: RiskBreakdown


# ============================================================================
# Legacy schemas (for backward compatibility)
# ============================================================================

class RelatedCaseResponse(BaseModel):
    """Legacy schema for backward compatibility."""
    
    case_id: str
    incident_id: str
    distance_meters: float
    matched_tags: List[str]


class SuspectedPersonResponse(BaseModel):
    """Legacy schema for backward compatibility."""
    
    person_id: str
    name: str
    match_score: float
    cases_count: int
    matched_tags: List[str]


class IntelligenceResponse(BaseModel):
    """Legacy response schema."""
    
    related_cases: List[RelatedCaseResponse]
    suspected_persons: List[SuspectedPersonResponse]
