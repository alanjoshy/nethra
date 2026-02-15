"""
Incident schemas for request/response validation.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field, field_validator


class IncidentCreateRequest(BaseModel):
    """Request schema for creating an incident."""
    
    incident_type: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    occurred_at: datetime
    longitude: float = Field(..., ge=-180, le=180)
    latitude: float = Field(..., ge=-90, le=90)
    notes: Optional[str] = None


class IncidentUpdateRequest(BaseModel):
    """Request schema for updating an incident."""
    
    incident_type: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    occurred_at: Optional[datetime] = None
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    notes: Optional[str] = None


class IncidentResponse(BaseModel):
    """Response schema for incident data."""
    
    id: str
    reported_by: str
    incident_type: str
    description: Optional[str] = None
    occurred_at: datetime
    longitude: float
    latitude: float
    created_at: datetime
    notes: Optional[str] = None

    @field_validator('id', 'reported_by', mode='before')
    @classmethod
    def convert_uuid_to_str(cls, v):
        """Convert UUID to string."""
        if isinstance(v, UUID):
            return str(v)
        return v

    model_config = {
        "from_attributes": True
    }
