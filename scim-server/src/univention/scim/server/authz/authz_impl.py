# src/univention/scim/server/authz/authz.py
# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH
from abc import ABC, abstractmethod
from typing import Any

from fastapi import Request


class Authz(ABC):
    """
    Interface for authorization.
    """

    @abstractmethod
    async def authorize(self, request: Request, user: dict[str, Any], resource_type: str) -> bool:
        """
        Authorize a request.
        Args:
            request: The request to authorize
            user: The authenticated user's information
            resource_type: The type of resource being accessed
        Returns:
            True if authorized, False otherwise
        """
        pass
