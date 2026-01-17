"""
Common utilities and shared components for Nethra Backend.

This module exports commonly used classes, functions, and constants.
"""

from app.common.constants import (
    UserRole,
    CaseStatus,
    IncidentType,
    IncidentPriority,
    MediaType,
    Pagination,
    Auth,
)

from app.common.exceptions import (
    NethraException,
    AuthenticationError,
    AuthorizationError,
    NotFoundError,
    ValidationError,
    ConflictError,
    DatabaseError,
    ExternalServiceError,
)

from app.common.responses import (
    SuccessResponse,
    ErrorResponse,
    PaginatedResponse,
    PaginationMeta,
    TokenResponse,
    MessageResponse,
)

from app.common.pagination import (
    PaginationParams,
    PaginatedResult,
    paginate,
)

from app.common.logging import (
    setup_logging,
    get_logger,
    LoggerMixin,
)

__all__ = [
    # Constants
    "UserRole",
    "CaseStatus",
    "IncidentType",
    "IncidentPriority",
    "MediaType",
    "Pagination",
    "Auth",
    
    # Exceptions
    "NethraException",
    "AuthenticationError",
    "AuthorizationError",
    "NotFoundError",
    "ValidationError",
    "ConflictError",
    "DatabaseError",
    "ExternalServiceError",
    
    # Responses
    "SuccessResponse",
    "ErrorResponse",
    "PaginatedResponse",
    "PaginationMeta",
    "TokenResponse",
    "MessageResponse",
    
    # Pagination
    "PaginationParams",
    "PaginatedResult",
    "paginate",
    
    # Logging
    "setup_logging",
    "get_logger",
    "LoggerMixin",
]
