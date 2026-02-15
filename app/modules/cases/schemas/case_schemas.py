"""
Case schemas for request/response validation.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field, field_validator


class CaseCreateRequest(BaseModel):
    """Request schema for creating a case."""
    
    primary_incident_id: UUID
    title: str = Field(..., min_length=1, max_length=255)
    status: str = Field(..., pattern="^(open|investigating|closed|archived)$")
    notes: Optional[str] = Field(None, max_length=1000)


class CaseUpdateRequest(BaseModel):
    """Request schema for updating a case."""
    
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    notes: Optional[str] = Field(None, max_length=1000)


class CaseStatusUpdateRequest(BaseModel):
    """Request schema for updating case status."""
    
    new_status: str = Field(..., pattern="^(open|investigating|closed|archived)$")


class CaseResponse(BaseModel):
    """Response schema for case data."""
    
    id: str
    primary_incident_id: str
    title: str
    status: str
    created_at: datetime
    notes: Optional[str] = None

    @field_validator('id', 'primary_incident_id', mode='before')
    @classmethod
    def convert_uuid_to_str(cls, v):
        """Convert UUID to string."""
        if isinstance(v, UUID):
            return str(v)
        return v

    model_config = {
        "from_attributes": True
    }


class CaseStatusHistoryResponse(BaseModel):
    """Response schema for case status history."""
    
    id: str
    case_id: str
    old_status: str
    new_status: str
    changed_by: str
    changed_at: datetime

    @field_validator('id', 'case_id', 'changed_by', mode='before')
    @classmethod
    def convert_uuid_to_str(cls, v):
        """Convert UUID to string."""
        if isinstance(v, UUID):
            return str(v)
        return v

    model_config = {
        "from_attributes": True
    }
