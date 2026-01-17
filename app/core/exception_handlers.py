"""
Global exception handlers for the application.
"""

from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from app.common.exceptions import NethraException
from app.common.responses import ErrorResponse


async def nethra_exception_handler(request: Request, exc: NethraException) -> JSONResponse:
    """
    Handle custom Nethra exceptions.
    
    Args:
        request: FastAPI request
        exc: Custom exception
    
    Returns:
        JSON response with error details
    """
    error_response = ErrorResponse(
        error=exc.error_code,
        message=exc.message,
        details=exc.details
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response.model_dump()
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """
    Handle Pydantic validation errors.
    
    Args:
        request: FastAPI request
        exc: Validation error
    
    Returns:
        JSON response with validation error details
    """
    error_response = ErrorResponse(
        error="VALIDATION_ERROR",
        message="Invalid request data",
        details={"errors": exc.errors()}
    )
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=error_response.model_dump()
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Handle unexpected exceptions.
    
    Args:
        request: FastAPI request
        exc: Unhandled exception
    
    Returns:
        JSON response with generic error
    """
    error_response = ErrorResponse(
        error="INTERNAL_ERROR",
        message="An unexpected error occurred",
        details={"error": str(exc)} if isinstance(exc, Exception) else None
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error_response.model_dump()
    )
