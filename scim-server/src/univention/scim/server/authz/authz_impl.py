# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

import time
from datetime import UTC, datetime
from typing import Any

from fastapi import HTTPException, Request, status
from loguru import logger
from univention.admin.rest.client import UDM

from univention.scim.server.authz.authz import Authorization
from univention.scim.server.config import UdmConfig


class AllowGroup(Authorization):
    """
    Allow access if user is in a specific group.
    """

    def __init__(self, group_dn: str, udm_settings: UdmConfig):
        self.group_dn = group_dn
        self.valid_user_cache: dict[str, int] = {}

        # Initialize UDM client
        self.udm_client = UDM.http(f"{udm_settings.url.rstrip('/')}/", udm_settings.username, udm_settings.password)

    def _check_cache(self, user: dict[str, Any]) -> bool:
        cache_to_delete = set()
        for username, expires in self.valid_user_cache.items():
            if not expires:
                continue

            current_time = int(time.time())
            if expires < current_time:
                logger.debug(
                    "Remove outdated cache",
                    user=username,
                    expires=datetime.fromtimestamp(expires, tz=UTC),
                    current_time=datetime.fromtimestamp(current_time, tz=UTC),
                )
                cache_to_delete.add(username)

        for username in cache_to_delete:
            del self.valid_user_cache[username]

        return user["username"] in self.valid_user_cache

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

        if self._check_cache(user):
            logger.debug(
                "Succesfully validated user by cache",
                user=user["username"],
                expires=datetime.fromtimestamp(user["expires"], tz=UTC),
            )
            return True

        module = self.udm_client.get("users/user")
        results = list(module.search(f"username={user['username']}"))
        if len(results) == 0:
            logger.error("User not found in UDM", user=user["username"], results=results)
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Missing access rights.")

        if len(results) != 1:
            logger.error("More than one user found in UDM", user=user["username"], results=results)
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Missing access rights.")

        udm_user = results[0].open()
        if self.group_dn not in udm_user.properties["groups"]:
            logger.error("User not in mandatory group", user=user["username"], group=self.group_dn, udm_user=udm_user)
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Missing access rights.")

        logger.debug(
            "Succesfully validated user", user=user["username"], expires=datetime.fromtimestamp(user["expires"], tz=UTC)
        )
        self.valid_user_cache[user["username"]] = user["expires"]
        return True
