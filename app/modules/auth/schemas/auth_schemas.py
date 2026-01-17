"""
Authentication module schemas.
"""

from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    """Login request schema."""
    
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=1, description="User password")
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "admin@nethra.gov",
                "password": "securepassword123"
            }
        }


class UserResponse(BaseModel):
    """User response schema."""
    
    id: str = Field(..., description="User ID")
    name: str = Field(..., description="User full name")
    email: str = Field(..., description="User email")
    role: str = Field(..., description="User role (admin/officer/analyst)")
    is_active: bool = Field(..., description="Whether the user is active")
    created_at: str = Field(..., description="User creation timestamp")
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "name": "John Doe",
                "email": "john@nethra.gov",
                "role": "admin",
                "is_active": True,
                "created_at": "2024-01-01T00:00:00"
            }
        }


class LoginResponse(BaseModel):
    """Login response with token and user data."""
    
    access_token: str = Field(..., description="Access token")
    token_type: str = Field(default="bearer", description="Token type")
    user: UserResponse = Field(..., description="Authenticated user data")
    
    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "v4.local.xxx...",
                "token_type": "bearer",
                "user": {
                    "id": "123e4567-e89b-12d3-a456-426614174000",
                    "name": "John Doe",
                    "email": "john@nethra.gov",
                    "role": "admin",
                    "is_active": True,
                    "created_at": "2024-01-01T00:00:00"
                }
            }
        }
