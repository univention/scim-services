# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

import json
from collections.abc import Awaitable, Callable
from typing import Any

from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from lancelog import LogLevel
from loguru import logger

from univention.scim.server.config import application_settings


def setup_request_logging_middleware(app: FastAPI) -> None:
    """
    Setup request logging middleware for the FastAPI application.
    This approach uses FastAPI's built-in middleware system.
    """
    settings = application_settings()

    @app.middleware("http")
    async def request_logging_middleware(
        request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        # Only proceed with detailed logging if log level is DEBUG or more verbose
        should_log_details = settings.log_level.value <= LogLevel.DEBUG.value

        # Log the incoming request
        if should_log_details:
            await _log_request(request)

        # Process the request through the application
        response = await call_next(request)

        # Log the response
        if should_log_details:
            await _log_response(request, response)

        return response


async def _log_request(request: Request) -> None:
    """Log request details including path, method, and parameters."""
    log_data: dict[str, Any] = {
        "method": request.method,
        "path": request.url.path,
        "client": request.client.host if request.client else "unknown",
    }

    # Log query parameters
    if request.query_params:
        log_data["query_params"] = dict(request.query_params)

    # Log request headers (excluding sensitive headers)
    headers = dict(request.headers)
    if "authorization" in headers:
        headers["authorization"] = "[REDACTED]"
    log_data["headers"] = headers

    # Log body for POST/PUT/PATCH requests
    if request.method in ["POST", "PUT", "PATCH"]:
        try:
            body = await request.body()
            if body:
                try:
                    # Try to parse as JSON for prettier logging
                    json_body = json.loads(body)
                    # Redact sensitive information
                    if isinstance(json_body, dict) and "password" in json_body:
                        json_body["password"] = "[REDACTED]"
                    log_data["body"] = json_body
                except json.JSONDecodeError:
                    # If not JSON, log as string with length limit
                    body_text = body.decode("utf-8", errors="replace")
                    log_data["body"] = f"{body_text[:1000]}..." if len(body_text) > 1000 else body_text

        except Exception as e:
            log_data["body_error"] = f"Error reading body: {str(e)}"

    logger.debug("SCIM Request", **log_data)


async def _log_response(request: Request, response: Response) -> None:
    """Log response details including status code and body if applicable."""
    log_data: dict[str, Any] = {
        "method": request.method,
        "path": request.url.path,
        "status_code": response.status_code,
    }

    # Log response headers (excluding sensitive headers)
    headers = dict(response.headers)
    log_data["headers"] = headers

    # Log response body for JSON responses
    if isinstance(response, JSONResponse):
        try:
            # Access the raw content directly
            body = response.body
            if body:
                try:
                    # Try to parse as JSON for prettier logging
                    json_body = json.loads(body)
                    log_data["response_body"] = json_body
                except json.JSONDecodeError:
                    # If not JSON, log as string with length limit
                    if isinstance(body, bytes):
                        body_text = body.decode("utf-8", errors="replace")
                    else:
                        # Handle memoryview case
                        body_text = bytes(body).decode("utf-8", errors="replace")
                    log_data["response_body"] = f"{body_text[:1000]}..." if len(body_text) > 1000 else body_text
        except Exception as e:
            log_data["response_body_error"] = f"Error reading response body: {str(e)}"

    logger.debug("SCIM Response", **log_data)
