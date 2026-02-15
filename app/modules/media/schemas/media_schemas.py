"""
Media schemas for request/response validation.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field, field_validator


class MediaCreateRequest(BaseModel):
    """Request schema for creating/uploading media."""
    
    case_id: UUID
    file_path: str = Field(..., min_length=1)
    media_type: str = Field(..., min_length=1, max_length=50)
    camera_type: Optional[str] = Field(None, max_length=100)
    capture_time: Optional[datetime] = None


class MediaResponse(BaseModel):
    """Response schema for media data."""
    
    id: str
    case_id: str
    file_path: str
    media_type: str
    camera_type: Optional[str] = None
    capture_time: Optional[datetime] = None
    uploaded_at: datetime

    @field_validator('id', 'case_id', mode='before')
    @classmethod
    def convert_uuid_to_str(cls, v):
        """Convert UUID to string."""
        if isinstance(v, UUID):
            return str(v)
        return v

    model_config = {
        "from_attributes": True
    }
