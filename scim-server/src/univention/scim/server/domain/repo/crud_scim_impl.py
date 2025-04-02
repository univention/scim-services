# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH
import copy
from typing import Generic, TypeVar, cast
from uuid import uuid4

from loguru import logger
from scim2_models import Resource
from univention.scim.server.domain.crud_scim import CrudScim


T = TypeVar("T", bound=Resource)


class CrudScimImpl(Generic[T], CrudScim[T]):
    """
    In-memory implementation of the CrudScim interface.
    This implementation is for development and testing purposes.
    It stores resources in memory and does not persist them.
    """

    def __init__(self) -> None:
        """Initialize the repository with an empty collection."""
        self.resources: dict[str, Resource] = {}

    async def get(self, resource_id: str) -> T:
        """Get a resource by ID."""
        logger.debug(f"Getting resource by ID: {resource_id}")
        result = self.resources.get(resource_id)
        if result is None:
            raise ValueError(f"Resource with ID {resource_id} not found")
        return cast(T, result)

    async def list(self, filter_str: str | None = None, start_index: int = 1, count: int | None = None) -> list[T]:
        """List resources with optional filtering and pagination."""
        logger.debug(f"Listing resources with filter: {filter_str}")
        # TODO: Implement real filtering
        resources = list(self.resources.values())
        # Apply pagination
        start_idx = start_index - 1  # Convert to 0-based
        resources = resources[start_idx : start_idx + count] if count is not None else resources[start_idx:]
        return cast(list[T], resources)

    async def count(self, filter_str: str | None = None) -> int:
        """Count resources matching a filter."""
        logger.debug(f"Counting resources with filter: {filter_str}")
        # TODO: Implement real filtering
        return len(self.resources)

    async def create(self, resource: T) -> T:
        """Create a new resource."""
        logger.debug("Creating new resource")
        # Generate ID if not provided
        if not resource.id:
            resource.id = str(uuid4())
        # Store a copy to prevent external modification
        self.resources[resource.id] = copy.deepcopy(resource)
        return cast(T, self.resources[resource.id])

    async def update(self, resource_id: str, resource: T) -> T:
        """Update an existing resource."""
        logger.debug(f"Updating resource with ID: {resource_id}")
        if resource_id not in self.resources:
            raise ValueError(f"Resource with ID {resource_id} not found")
        # Ensure ID matches
        resource.id = resource_id
        # Store a copy to prevent external modification
        self.resources[resource_id] = copy.deepcopy(resource)
        return cast(T, self.resources[resource_id])

    async def delete(self, resource_id: str) -> bool:
        """Delete a resource."""
        logger.debug(f"Deleting resource with ID: {resource_id}")
        if resource_id in self.resources:
            del self.resources[resource_id]
            return True
        return False
