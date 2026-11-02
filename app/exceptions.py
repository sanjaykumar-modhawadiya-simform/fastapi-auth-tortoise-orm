"""
Custom Exceptions and Exception Handlers Module.

Defines custom domain exceptions and sets up global handlers to standardize error responses.
"""

from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

class EntityNotFoundException(Exception):
    """Custom exception raised when a requested database entity is not found."""
    def __init__(self, entity_name: str, identifier: str | int):
        self.entity_name = entity_name
        self.identifier = identifier

async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """
    Global custom handler for Pydantic/FastAPI input validation errors.
    Returns standard error format with HTTP 422.
    """
    formatted_errors = []
    for error in exc.errors():
        field = " -> ".join([str(loc) for loc in error.get("loc", [])])
        formatted_errors.append({"field": field, "message": error.get("msg")})

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "error_type": "ValidationError",
            "message": "Input validation failed",
            "details": formatted_errors
        }
    )

async def entity_not_found_exception_handler(request: Request, exc: EntityNotFoundException) -> JSONResponse:
    """
    Global handler for custom EntityNotFoundException.
    Returns standard HTTP 404 response.
    """
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={
            "success": False,
            "error_type": "NotFound",
            "message": f"{exc.entity_name} with identifier '{exc.identifier}' was not found."
        }
    )