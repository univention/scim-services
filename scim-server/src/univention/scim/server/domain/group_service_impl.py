# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH
from uuid import uuid4

from loguru import logger
from scim2_models import Group, ListResponse
from univention.scim.server.domain.crud_scim import CrudScim
from univention.scim.server.domain.group_service import GroupService


class GroupServiceImpl(GroupService):
    """
    Implementation of the GroupService interface.
    Provides domain logic for group management operations.
    """

    def __init__(self, group_repository: CrudScim):
        """
        Initialize the group service.
        Args:
            group_repository: Repository for group data
        """
        self.group_repository = group_repository

    async def get_group(self, group_id: str) -> Group:
        """Get a group by ID."""
        logger.debug(f"Getting group with ID: {group_id}")
        group = await self.group_repository.get(group_id)
        if not group:
            raise ValueError(f"Group with ID {group_id} not found")
        return group

    async def list_groups(
        self, filter_str: str | None = None, start_index: int = 1, count: int | None = None
    ) -> ListResponse[Group]:
        """List groups with optional filtering and pagination."""
        logger.debug(f"Listing groups with filter: {filter_str}, start_index: {start_index}, count: {count}")
        groups = await self.group_repository.list(filter_str, start_index, count)
        total = await self.group_repository.count(filter_str)
        return ListResponse[Group](
            schemas=["urn:ietf:params:scim:api:messages:2.0:ListResponse"],
            total_results=total,
            resources=groups,
            start_index=start_index,
            items_per_page=len(groups),
        )

    async def create_group(self, group: Group) -> Group:
        """Create a new group."""
        logger.debug("Creating new group")
        # Validate group data
        self._validate_group(group)
        # Generate ID if not provided
        if not group.id:
            group.id = str(uuid4())
        # Create group in repository
        created_group = await self.group_repository.create(group)
        logger.info(f"Created group with ID: {created_group.id}")
        return created_group

    async def update_group(self, group_id: str, group: Group) -> Group:
        """Update an existing group."""
        logger.debug(f"Updating group with ID: {group_id}")
        # Check if group exists
        existing_group = await self.group_repository.get(group_id)
        if not existing_group:
            raise ValueError(f"Group with ID {group_id} not found")
        # Validate group data
        self._validate_group(group)
        # Ensure ID matches
        group.id = group_id
        # Update group in repository
        updated_group = await self.group_repository.update(group_id, group)
        logger.info(f"Updated group with ID: {group_id}")
        return updated_group

    async def delete_group(self, group_id: str) -> bool:
        """Delete a group."""
        logger.debug(f"Deleting group with ID: {group_id}")
        # Check if group exists
        existing_group = await self.group_repository.get(group_id)
        if not existing_group:
            raise ValueError(f"Group with ID {group_id} not found")
        # Delete group from repository
        result = await self.group_repository.delete(group_id)
        if result:
            logger.info(f"Deleted group with ID: {group_id}")
        return bool(result)

    def _validate_group(self, group: Group) -> None:
        """
        Validate group data.
        Args:
            group: The group to validate
        Raises:
            ValueError: If validation fails
        """
        # Validate required fields
        if not group.display_name:
            raise ValueError("displayName is required")
