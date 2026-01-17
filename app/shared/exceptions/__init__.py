"""
Shared exception classes.
"""

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

__all__ = [
    "NethraException",
    "AuthenticationError",
    "AuthorizationError",
    "NotFoundError",
    "ValidationError",
    "ConflictError",
    "DatabaseError",
    "ExternalServiceError",
]
