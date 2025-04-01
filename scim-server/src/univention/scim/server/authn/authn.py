# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH
from abc import ABC, abstractmethod

from fastapi import Request


class Authentication(ABC):
    """
    Interface for authentication providers.

    Implementations should verify credentials and return user information.
    """

    @abstractmethod
    async def authenticate(self, request: Request) -> dict:
        """
        Authenticate a request.

        Args:
            request: The FastAPI request object

        Returns:
            dict: User information if authentication succeeds

        Raises:
            HTTPException: If authentication fails
        """
        pass
