"""
Intelligence schemas for request/response validation.
"""

from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field, field_validator


class RelatedCaseResponse(BaseModel):
    """Schema for a related case found via intelligence search."""
    
    case_id: str
    incident_id: str
    distance_meters: float
    matched_tags: list[str]

    @field_validator('case_id', 'incident_id', mode='before')
    @classmethod
    def convert_uuid_to_str(cls, v):
        """Convert UUID to string."""
        if isinstance(v, UUID):
            return str(v)
        return v


class SuspectedPersonResponse(BaseModel):
    """Schema for a suspected person linked to related cases."""
    
    person_id: str
    name: str
    match_score: float
    cases_count: int
    matched_tags: list[str]

    @field_validator('person_id', mode='before')
    @classmethod
    def convert_uuid_to_str(cls, v):
        """Convert UUID to string."""
        if isinstance(v, UUID):
            return str(v)
        return v


class IntelligenceResponse(BaseModel):
    """Main response schema for intelligence search."""
    
    related_cases: list[RelatedCaseResponse]
    suspected_persons: list[SuspectedPersonResponse]
