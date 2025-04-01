# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH
from fastapi import HTTPException, Request, status
from loguru import logger
from univention.scim.server.authn.authn import Authentication


class BasicAuthentication(Authentication):
    """
    Implements basic authentication for the SCIM API.

    This is a placeholder implementation for development purposes.
    """

    async def authenticate(self, request: Request) -> dict:
        """
        Authenticate using HTTP Basic authentication.

        Args:
            request: The FastAPI request object

        Returns:
            dict: User information if authentication succeeds

        Raises:
            HTTPException: If authentication fails
        """
        # Example implementation
        auth_header = request.headers.get("Authorization")

        if not auth_header or not auth_header.startswith("Basic "):
            logger.warning("Missing or invalid Authorization header")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Basic"},
            )

        # In a real implementation, decode and validate credentials
        # For now, return a dummy user
        return {"username": "admin", "roles": ["admin"]}
