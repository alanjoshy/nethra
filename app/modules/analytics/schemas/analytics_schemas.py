"""
Analytics schemas for aggregated reporting.
"""

from typing import List
from pydantic import BaseModel, Field


# ============================================================================
# Crime by Location
# ============================================================================

class DistrictStats(BaseModel):
    """District-level crime statistics."""
    
    district: str = Field(description="District/region name")
    incident_count: int = Field(description="Number of incidents")


class CrimeByLocationResponse(BaseModel):
    """Crime by location aggregation response."""
    
    districts: List[DistrictStats] = Field(default_factory=list)


# ============================================================================
# Pattern Frequency
# ============================================================================

class PatternStats(BaseModel):
    """Tag/pattern frequency statistics."""
    
    tag: str = Field(description="Tag name")
    count: int = Field(description="Occurrence count")


class PatternFrequencyResponse(BaseModel):
    """Pattern frequency aggregation response."""
    
    patterns: List[PatternStats] = Field(default_factory=list)


# ============================================================================
# Monthly Trends
# ============================================================================

class MonthlyData(BaseModel):
    """Monthly crime statistics."""
    
    month: str = Field(description="Month name")
    incident_count: int = Field(description="Incident count for month")


class MonthlyTrendsResponse(BaseModel):
    """Monthly crime trends response."""
    
    year: int = Field(description="Year of analysis")
    monthly_data: List[MonthlyData] = Field(default_factory=list)


# ============================================================================
# Repeat Offender Overview
# ============================================================================

class RepeatOffenderSummary(BaseModel):
    """Repeat offender summary statistics."""
    
    person_id: str = Field(description="Person UUID")
    name: str = Field(description="Person name")
    case_count: int = Field(description="Number of cases involved in")


class RepeatOffenderOverviewResponse(BaseModel):
    """Repeat offender overview response."""
    
    repeat_offenders: List[RepeatOffenderSummary] = Field(default_factory=list)
