"""
Person schemas for request/response validation.
"""

from datetime import date, datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field, field_validator
from app.modules.persons.entities.person_entity import PersonRole


class PersonCreateRequest(BaseModel):
    """Request schema for creating a person."""
    
    name: str = Field(..., min_length=1, max_length=255)
    date_of_birth: Optional[date] = None
    phone: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = None
    identification_number: Optional[str] = Field(None, max_length=50)


class PersonUpdateRequest(BaseModel):
    """Request schema for updating a person."""
    
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    date_of_birth: Optional[date] = None
    phone: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = None
    identification_number: Optional[str] = Field(None, max_length=50)


class PersonResponse(BaseModel):
    """Response schema for person data."""
    
    id: str
    name: str
    date_of_birth: Optional[date] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    identification_number: Optional[str] = None
    created_at: datetime
    updated_at: datetime

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


class CasePersonLinkRequest(BaseModel):
    """Request schema for linking a person to a case."""
    
    person_id: UUID
    role: PersonRole


class CasePersonResponse(BaseModel):
    """Response schema for case-person link."""
    
    id: str
    case_id: str
    person_id: str
    role: str
    person: Optional[PersonResponse] = None

    @field_validator('id', 'case_id', 'person_id', mode='before')
    @classmethod
    def convert_uuid_to_str(cls, v):
        """Convert UUID to string."""
        if isinstance(v, UUID):
            return str(v)
        return v

    model_config = {
        "from_attributes": True
    }
