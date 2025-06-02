# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

from fastapi import HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from loguru import logger
from scim2_models import Error


async def scim_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """
    Custom exception handler for SCIM-compliant error responses.

    This ensures all error responses follow the SCIM error format with the correct schemas.
    """
    logger.debug("HTTP exception", code=exc.status_code, details=exc.detail)

    # Check if the exception already has a SCIM-formatted error detail
    if isinstance(exc.detail, dict) and "schemas" in exc.detail:
        # Already formatted as SCIM error
        return JSONResponse(
            status_code=exc.status_code,
            content=exc.detail,
        )

    # Create a proper SCIM error response
    error = Error(
        status=exc.status_code,
        detail=str(exc.detail),
        schemas=["urn:ietf:params:scim:api:messages:2.0:Error"],
    )

    # Add scimType if provided
    if hasattr(exc, "scim_type"):
        error.scim_type = exc.scim_type

    return JSONResponse(
        status_code=exc.status_code,
        content=error.model_dump(exclude_none=True),
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Generic exception handler for any unhandled exceptions.

    Converts any exception to a proper SCIM error response.
    """
    logger.exception("Unhandled exception", exception=exc)
    error = Error(
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=str(exc),
        schemas=["urn:ietf:params:scim:api:messages:2.0:Error"],
    )
    return JSONResponse(status_code=error.status, content=error.model_dump(exclude_none=True))


async def fastapi_request_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """
    Custom exception handler for request validation errors.

    This ensures the error responses follow the SCIM error format and is logged with DEBUG logging.
    """
    logger.debug("Request validation error", details=exc.errors())
    error = Error(
        status=status.HTTP_422_UNPROCESSABLE_ENTITY,
        detail=str(exc),
        schemas=["urn:ietf:params:scim:api:messages:2.0:Error"],
    )
    return JSONResponse(status_code=error.status, content=error.model_dump(exclude_none=True))
