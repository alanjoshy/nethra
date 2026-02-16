"""
Search schemas for unified advanced search.
"""

from typing import Optional, List, Dict
from datetime import date, datetime
from uuid import UUID
from pydantic import BaseModel, Field


class SearchResultItem(BaseModel):
    """Individual search result item."""
    
    case_id: str = Field(description="Case UUID")
    incident_type: str = Field(description="Incident type/category")
    occurred_at: datetime = Field(description="When incident occurred")
    location: Dict[str, float] = Field(description="Location coordinates {lat, lng}")
    tags: List[str] = Field(default_factory=list, description="Associated tags")
    suspects: List[str] = Field(default_factory=list, description="Suspect names")
    status: str = Field(description="Case status")


class SearchResponse(BaseModel):
    """Unified search response."""
    
    total_results: int = Field(description="Total number of matching results")
    results: List[SearchResultItem] = Field(default_factory=list)
