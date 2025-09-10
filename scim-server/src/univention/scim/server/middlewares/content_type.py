# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

from collections.abc import Awaitable, Callable

from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware


class ContentTypeMiddleware(BaseHTTPMiddleware):
    """
    Middleware to handle SCIM content type negotiation.

    - Accepts both application/json and application/scim+json for incoming requests
    - Sets response content type based on Accept header, defaulting to application/scim+json
    """

    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        # Allow both content types for incoming requests
        content_type = request.headers.get("content-type", "").lower()
        if content_type.startswith("application/json"):
            # FastAPI will handle the JSON parsing regardless of whether it's application/json
            # or application/scim+json, so no modification needed for request processing
            pass

        # Process the request
        response: Response = await call_next(request)

        # Set response content type based on Accept header
        accept_header = request.headers.get("accept", "").lower()

        # Only modify content type for JSON responses (not for HTML docs, etc.)
        if response.headers.get("content-type", "").startswith("application/json"):
            if "application/json" in accept_header and "application/scim+json" not in accept_header:
                # Client explicitly wants application/json and not SCIM
                response.headers["content-type"] = "application/json; charset=utf-8"
            else:
                # Default to SCIM content type or if client accepts SCIM
                response.headers["content-type"] = "application/scim+json; charset=utf-8"

        return response


def add_content_type_middleware(app: FastAPI) -> None:
    """Add content type middleware to FastAPI app."""
    app.add_middleware(ContentTypeMiddleware)
