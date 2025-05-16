# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

from abc import ABC, abstractmethod
from typing import Any

from fastapi import Request


class Authorization(ABC):
    """
    Interface for authorization.
    """

    @abstractmethod
    async def authorize(self, request: Request, user: dict[str, Any]) -> bool:
        """
        Authorize a request.
        Args:
            request: The request to authorize
            user: The authenticated user's information
        Returns:
            True if authorized, False otherwise
        """
        pass
