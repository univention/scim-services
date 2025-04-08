# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH
from __future__ import annotations

from typing import Generic, TypeVar, cast

from loguru import logger
from scim2_models import Resource
from univention.scim.server.domain.crud_scim import CrudScim


T = TypeVar("T", bound=Resource)


class CrudManager(Generic[T], CrudScim[T]):
    """
    Manager that coordinates access to underlying repositories.
    This class handles CRUD operations by delegating to the appropriate repository
    implementations, providing a single access point for resource management.
    """

    def __init__(self, primary_repository: CrudScim[T], resource_type: str):
        """
        Initialize the CRUD manager.
        Args:
            primary_repository: The primary repository to use for CRUD operations (e.g., UDM)
            resource_type: The type of resource being managed (e.g., 'User', 'Group')
        """
        self.primary_repository = primary_repository
        self.resource_type = resource_type
        self.logger = logger.bind(resource_type=resource_type)
        self.logger.info("Initialized CRUD manager.")

    async def get(self, resource_id: str) -> T:
        """Get a resource by ID."""
        self.logger.trace("Getting resource.", id=resource_id)
        try:
            resource = await self.primary_repository.get(resource_id)
            return cast(T, resource)
        except Exception as exc:
            raise ValueError(f"Resource with ID {resource_id} not found") from exc

    async def list(self, filter_str: str | None = None, start_index: int = 1, count: int | None = None) -> list[T]:
        """List resources with optional filtering and pagination."""
        self.logger.trace("Listing resources", filter_str=filter_str)
        # For now, we're just using the primary repository for listing
        resources = await self.primary_repository.list(filter_str, start_index, count)
        return cast(list[T], resources)

    async def count(self, filter_str: str | None = None) -> int:
        """Count resources matching a filter."""
        self.logger.trace("Counting resources", filter_str=filter_str)
        # For now, we're just using the primary repository for counting
        result = await self.primary_repository.count(filter_str)
        return cast(int, result)

    async def create(self, resource: T) -> T:
        """Create a new resource."""
        self.logger.trace("Creating resource")
        # Create in the primary repository
        created_resource = await self.primary_repository.create(resource)
        return cast(T, created_resource)

    async def update(self, resource_id: str, resource: T) -> T:
        """Update an existing resource."""
        self.logger.trace("Updating resource", id=resource_id)
        # Update in the primary repository
        updated_resource = await self.primary_repository.update(resource_id, resource)
        return cast(T, updated_resource)

    async def delete(self, resource_id: str) -> bool:
        """Delete a resource."""
        self.logger.trace("Deleting resource", id=resource_id)
        # Delete from the primary repository
        result = await self.primary_repository.delete(resource_id)
        return bool(result)
