"""
Standardized API response models using Pydantic.
"""

from typing import Any, Generic, Optional, TypeVar
from pydantic import BaseModel, Field


DataT = TypeVar("DataT")


class SuccessResponse(BaseModel, Generic[DataT]):
    """Standard success response wrapper."""
    
    success: bool = Field(default=True, description="Indicates if the request was successful")
    data: DataT = Field(..., description="Response data")
    message: Optional[str] = Field(default=None, description="Optional success message")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "data": {"id": "123", "name": "Example"},
                "message": "Operation completed successfully"
            }
        }


class ErrorResponse(BaseModel):
    """Standard error response."""
    
    success: bool = Field(default=False, description="Always false for errors")
    error: str = Field(..., description="Error code")
    message: str = Field(..., description="Human-readable error message")
    details: Optional[dict[str, Any]] = Field(default=None, description="Additional error details")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": False,
                "error": "VALIDATION_ERROR",
                "message": "Invalid input data",
                "details": {"field": "email", "reason": "Invalid format"}
            }
        }


class PaginatedResponse(BaseModel, Generic[DataT]):
    """Paginated response wrapper."""
    
    success: bool = Field(default=True, description="Indicates if the request was successful")
    data: list[DataT] = Field(..., description="List of items for current page")
    pagination: "PaginationMeta" = Field(..., description="Pagination metadata")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "data": [{"id": "1", "name": "Item 1"}, {"id": "2", "name": "Item 2"}],
                "pagination": {
                    "page": 1,
                    "page_size": 20,
                    "total_items": 45,
                    "total_pages": 3,
                    "has_next": True,
                    "has_previous": False
                }
            }
        }


class PaginationMeta(BaseModel):
    """Pagination metadata."""
    
    page: int = Field(..., description="Current page number (1-indexed)", ge=1)
    page_size: int = Field(..., description="Number of items per page", ge=1, le=100)
    total_items: int = Field(..., description="Total number of items", ge=0)
    total_pages: int = Field(..., description="Total number of pages", ge=0)
    has_next: bool = Field(..., description="Whether there is a next page")
    has_previous: bool = Field(..., description="Whether there is a previous page")


class TokenResponse(BaseModel):
    """Authentication token response."""
    
    access_token: str = Field(..., description="JWT/PASETO access token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: Optional[int] = Field(default=None, description="Token expiration time in seconds")
    
    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "v4.local.xxx...",
                "token_type": "bearer",
                "expires_in": 3600
            }
        }


class MessageResponse(BaseModel):
    """Simple message response."""
    
    success: bool = Field(default=True, description="Indicates if the request was successful")
    message: str = Field(..., description="Response message")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Operation completed successfully"
            }
        }
