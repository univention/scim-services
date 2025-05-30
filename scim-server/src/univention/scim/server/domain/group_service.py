# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

from abc import ABC, abstractmethod
from typing import Any

from scim2_models import Group, ListResponse


class GroupService(ABC):
    """
    Interface for group management operations.
    Defines the contract for group-related operations in the domain layer.
    """

    @abstractmethod
    async def get_group(self, group_id: str) -> Group:
        """
        Get a group by ID.
        Args:
            group_id: The group's unique identifier
        Returns:
            Group: The group object if found
        Raises:
            ValueError: If the group is not found
        """
        pass

    @abstractmethod
    async def list_groups(
        self, filter_str: str | None = None, start_index: int = 1, count: int | None = None
    ) -> ListResponse[Group]:
        """
        List groups with optional filtering and pagination.
        Args:
            filter_str: SCIM filter expression
            start_index: 1-based index for the first result
            count: Maximum number of results to return
        Returns:
            ListResponse: Paginated list of groups
        """
        pass

    @abstractmethod
    async def create_group(self, group: Group) -> Group:
        """
        Create a new group.
        Args:
            group: The group to create
        Returns:
            Group: The created group with generated ID
        Raises:
            ValueError: If the group is invalid or already exists
        """
        pass

    @abstractmethod
    async def update_group(self, group_id: str, group: Group) -> Group:
        """
        Update an existing group.
        Args:
            group_id: The group's unique identifier
            group: The updated group data
        Returns:
            Group: The updated group
        Raises:
            ValueError: If the group is not found or the update is invalid
        """
        pass

    @abstractmethod
    async def delete_group(self, group_id: str) -> bool:
        """
        Delete a group.
        Args:
            group_id: The group's unique identifier
        Returns:
            bool: True if the group was deleted
        Raises:
            ValueError: If the group is not found
        """
        pass

    @abstractmethod
    async def apply_patch_operations(self, group_id: str, operations: list[dict[str, Any]]) -> Group:
        pass
