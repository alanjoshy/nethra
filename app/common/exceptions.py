"""
Custom exception classes for Nethra Backend.
"""

from typing import Any, Optional


class NethraException(Exception):
    """Base exception for all custom exceptions."""
    
    def __init__(
        self,
        message: str,
        status_code: int = 500,
        error_code: Optional[str] = None,
        details: Optional[dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code or "INTERNAL_ERROR"
        self.details = details or {}
        super().__init__(self.message)


class AuthenticationError(NethraException):
    """Raised when authentication fails."""
    
    def __init__(self, message: str = "Authentication failed", details: Optional[dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=401,
            error_code="AUTHENTICATION_ERROR",
            details=details
        )


class AuthorizationError(NethraException):
    """Raised when user lacks required permissions."""
    
    def __init__(self, message: str = "Insufficient permissions", details: Optional[dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=403,
            error_code="AUTHORIZATION_ERROR",
            details=details
        )


class NotFoundError(NethraException):
    """Raised when a requested resource is not found."""
    
    def __init__(self, resource: str, identifier: Any = None):
        message = f"{resource} not found"
        if identifier:
            message += f": {identifier}"
        
        super().__init__(
            message=message,
            status_code=404,
            error_code="NOT_FOUND",
            details={"resource": resource, "identifier": str(identifier) if identifier else None}
        )


class ValidationError(NethraException):
    """Raised when input validation fails."""
    
    def __init__(self, message: str, field: Optional[str] = None, details: Optional[dict[str, Any]] = None):
        error_details = details or {}
        if field:
            error_details["field"] = field
        
        super().__init__(
            message=message,
            status_code=422,
            error_code="VALIDATION_ERROR",
            details=error_details
        )


class ConflictError(NethraException):
    """Raised when there's a conflict with existing data."""
    
    def __init__(self, message: str, details: Optional[dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=409,
            error_code="CONFLICT",
            details=details
        )


class DatabaseError(NethraException):
    """Raised when database operation fails."""
    
    def __init__(self, message: str = "Database operation failed", details: Optional[dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=500,
            error_code="DATABASE_ERROR",
            details=details
        )


class ExternalServiceError(NethraException):
    """Raised when an external service call fails."""
    
    def __init__(self, service: str, message: str = "External service unavailable", details: Optional[dict[str, Any]] = None):
        error_details = details or {}
        error_details["service"] = service
        
        super().__init__(
            message=message,
            status_code=503,
            error_code="EXTERNAL_SERVICE_ERROR",
            details=error_details
        )
