"""
Error codes and standardized error messages.
"""

from typing import TypedDict


class ErrorDetail(TypedDict):
    code: str
    message: str
    description: str


# Authentication Errors
AUTH_ERRORS = {
    "INVALID_CREDENTIALS": ErrorDetail(
        code="INVALID_CREDENTIALS",
        message="Invalid email or password",
        description="The provided credentials are incorrect"
    ),
    "TOKEN_EXPIRED": ErrorDetail(
        code="TOKEN_EXPIRED",
        message="Access token has expired",
        description="Your session has expired. Please login again"
    ),
    "TOKEN_INVALID": ErrorDetail(
        code="TOKEN_INVALID",
        message="Invalid access token",
        description="The provided token is malformed or invalid"
    ),
    "MISSING_TOKEN": ErrorDetail(
        code="MISSING_TOKEN",
        message="Authentication required",
        description="No authentication token provided"
    ),
}

# Authorization Errors
AUTHZ_ERRORS = {
    "INSUFFICIENT_PERMISSIONS": ErrorDetail(
        code="INSUFFICIENT_PERMISSIONS",
        message="Insufficient permissions",
        description="You don't have permission to perform this action"
    ),
    "ROLE_REQUIRED": ErrorDetail(
        code="ROLE_REQUIRED",
        message="Specific role required",
        description="This action requires specific role privileges"
    ),
}

# Validation Errors
VALIDATION_ERRORS = {
    "REQUIRED_FIELD": ErrorDetail(
        code="REQUIRED_FIELD",
        message="Required field missing",
        description="A required field is missing from the request"
    ),
    "INVALID_FORMAT": ErrorDetail(
        code="INVALID_FORMAT",
        message="Invalid format",
        description="The provided value has an invalid format"
    ),
    "INVALID_EMAIL": ErrorDetail(
        code="INVALID_EMAIL",
        message="Invalid email address",
        description="The provided email address is not valid"
    ),
    "INVALID_UUID": ErrorDetail(
        code="INVALID_UUID",
        message="Invalid UUID",
        description="The provided identifier is not a valid UUID"
    ),
}

# Resource Errors
RESOURCE_ERRORS = {
    "USER_NOT_FOUND": ErrorDetail(
        code="USER_NOT_FOUND",
        message="User not found",
        description="The requested user does not exist"
    ),
    "CASE_NOT_FOUND": ErrorDetail(
        code="CASE_NOT_FOUND",
        message="Case not found",
        description="The requested case does not exist"
    ),
    "INCIDENT_NOT_FOUND": ErrorDetail(
        code="INCIDENT_NOT_FOUND",
        message="Incident not found",
        description="The requested incident does not exist"
    ),
    "MEDIA_NOT_FOUND": ErrorDetail(
        code="MEDIA_NOT_FOUND",
        message="Media not found",
        description="The requested media file does not exist"
    ),
}

# Conflict Errors
CONFLICT_ERRORS = {
    "EMAIL_EXISTS": ErrorDetail(
        code="EMAIL_EXISTS",
        message="Email already exists",
        description="A user with this email address already exists"
    ),
    "DUPLICATE_ENTRY": ErrorDetail(
        code="DUPLICATE_ENTRY",
        message="Duplicate entry",
        description="This record already exists in the system"
    ),
}

# Database Errors
DATABASE_ERRORS = {
    "CONNECTION_FAILED": ErrorDetail(
        code="CONNECTION_FAILED",
        message="Database connection failed",
        description="Unable to connect to the database"
    ),
    "QUERY_FAILED": ErrorDetail(
        code="QUERY_FAILED",
        message="Database query failed",
        description="An error occurred while executing the database query"
    ),
}

# General Errors
GENERAL_ERRORS = {
    "INTERNAL_ERROR": ErrorDetail(
        code="INTERNAL_ERROR",
        message="Internal server error",
        description="An unexpected error occurred. Please try again later"
    ),
    "SERVICE_UNAVAILABLE": ErrorDetail(
        code="SERVICE_UNAVAILABLE",
        message="Service unavailable",
        description="The service is temporarily unavailable"
    ),
}
