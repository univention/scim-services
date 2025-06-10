# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

from abc import ABC, abstractmethod
from typing import Any

from scim2_models import ListResponse

from univention.scim.server.model_service.load_schemas_impl import UserWithExtensions


class UserService(ABC):
    """
    Interface for user management operations.
    Defines the contract for user-related operations in the domain layer.
    """

    @abstractmethod
    async def get_user(self, user_id: str) -> UserWithExtensions:
        """
        Get a user by ID.
        Args:
            user_id: The user's unique identifier
        Returns:
            User: The user object if found
        Raises:
            ValueError: If the user is not found
        """
        pass

    @abstractmethod
    async def list_users(
        self, filter_str: str | None = None, start_index: int = 1, count: int | None = None
    ) -> ListResponse[UserWithExtensions]:
        """
        List users with optional filtering and pagination.
        Args:
            filter_str: SCIM filter expression
            start_index: 1-based index for the first result
            count: Maximum number of results to return
        Returns:
            ListResponse: Paginated list of users
        """
        pass

    @abstractmethod
    async def create_user(self, user: UserWithExtensions) -> UserWithExtensions:
        """
        Create a new user.
        Args:
            user: The user to create
        Returns:
            User: The created user with generated ID
        Raises:
            ValueError: If the user is invalid or already exists
        """
        pass

    @abstractmethod
    async def update_user(self, user_id: str, user: UserWithExtensions) -> UserWithExtensions:
        """
        Update an existing user.
        Args:
            user_id: The user's unique identifier
            user: The updated user data
        Returns:
            User: The updated user
        Raises:
            ValueError: If the user is not found or the update is invalid
        """
        pass

    @abstractmethod
    async def delete_user(self, user_id: str) -> bool:
        """
        Delete a user.
        Args:
            user_id: The user's unique identifier
        Returns:
            bool: True if the user was deleted
        Raises:
            ValueError: If the user is not found
        """
        pass

    @abstractmethod
    async def apply_patch_operations(self, user_id: str, operations: list[dict[str, Any]]) -> UserWithExtensions:
        pass
