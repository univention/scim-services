# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH
from abc import ABC, abstractmethod

from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer


class Authentication(ABC):
    """
    Interface for authentication providers.

    Implementations should verify credentials and return user information.
    """

    @abstractmethod
    async def authenticate(self, credentials: HTTPAuthorizationCredentials) -> dict:
        """
        Authenticate credentions.

        Args:
            credentials: The FastAPI HTTPAuthorizationCredentials object

        Returns:
            dict: User information if authentication succeeds

        Raises:
            HTTPException: If authentication fails
        """
        pass
