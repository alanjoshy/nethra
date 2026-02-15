"""
Tag schemas for request/response validation.
"""

from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field, field_validator


class TagCreateRequest(BaseModel):
    """Request schema for creating a tag."""
    
    name: str = Field(..., min_length=1, max_length=50)


class TagResponse(BaseModel):
    """Response schema for tag data."""
    
    id: str
    name: str

    @field_validator('id', mode='before')
    @classmethod
    def convert_uuid_to_str(cls, v):
        """Convert UUID to string."""
        if isinstance(v, UUID):
            return str(v)
        return v

    model_config = {
        "from_attributes": True
    }


class IncidentTagLinkRequest(BaseModel):
    """Request schema for linking tags to an incident."""
    
    tags: list[str] = Field(..., min_length=1)  # List of tag names


class IncidentTagResponse(BaseModel):
    """Response schema for incident-tag link."""
    
    id: str
    incident_id: str
    tag_id: str
    tag: Optional[TagResponse] = None

    @field_validator('id', 'incident_id', 'tag_id', mode='before')
    @classmethod
    def convert_uuid_to_str(cls, v):
        """Convert UUID to string."""
        if isinstance(v, UUID):
            return str(v)
        return v

    model_config = {
        "from_attributes": True
    }
