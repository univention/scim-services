# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH
from abc import ABC, abstractmethod

from fastapi import Request


class Authorization(ABC):
    """
    Interface for authorization providers.

    Implementations should verify if the authenticated user has
    permission to perform the requested operation.
    """

    @abstractmethod
    async def authorize(self, request: Request, user: dict, resource_type: str, operation: str) -> bool:
        """
        Authorize an operation on a resource.

        Args:
            request: The FastAPI request object
            user: The authenticated user information
            resource_type: The type of resource being accessed (e.g., "User", "Group")
            operation: The operation being performed (e.g., "read", "create", "update", "delete")

        Returns:
            bool: True if the operation is authorized, False otherwise

        Raises:
            HTTPException: If authorization fails
        """
        pass
