# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

from abc import ABC, abstractmethod
from typing import Any


class Authentication(ABC):
    """
    Interface for authentication providers.

    Implementations should verify credentials and return user information.
    """

    @abstractmethod
    async def authenticate(self, token: str) -> dict[str, Any]:
        """
        Authenticate credentions.

        Args:
            token: The JWT token

        Returns:
            dict: User information if authentication succeeds
        """
        pass
