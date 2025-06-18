# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

from typing import Any

from fastapi import HTTPException, Request, status
from loguru import logger

from univention.scim.server.authz.authz import Authorization


class AllowAudience(Authorization):
    """
    Allow access if token has a specific audience set.
    """

    def __init__(self, audience: str):
        self.audience = audience

    async def authorize(self, request: Request, user: dict[str, Any]) -> bool:
        """
        Authorize a request.
        Args:
            request: The request to authorize
            user: The authenticated user's information
        Returns:
            True if authorized

        Raises:
            HTTPException: If validation fails
        """

        if self.audience in user["audience"]:
            logger.debug("Succesfully validated user", user=user)
            return True

        logger.error("Wrong audience claim", user=user)
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Missing access rights.")
