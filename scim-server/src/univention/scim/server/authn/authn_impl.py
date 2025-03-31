# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from loguru import logger
from univention.scim.server.authn.authn import Authentication


class AllowAllBearerAuthentication(Authentication):
    """
    Implements bearer authentication for the SCIM API.

    This is a placeholder implementation for development purposes.
    """

    async def authenticate(self, credentials: HTTPAuthorizationCredentials) -> dict:
        """
        Authenticate using HTTP Bearer authentication, allow all bearers.

        Args:
            credentials: The FastAPI HTTPAuthorizationCredentials object

        Returns:
            dict: User information if authentication succeeds

        Raises:
            HTTPException: If authentication fails
        """
        if not credentials:
            raise HTTPException(status_code=403, detail="Invalid authorization code.")

        if not credentials.scheme == "Bearer":
            raise HTTPException(status_code=403, detail="Invalid authentication scheme.")

        # Allow all tokens so no validation
        return {"username": "admin", "roles": ["admin"]}
