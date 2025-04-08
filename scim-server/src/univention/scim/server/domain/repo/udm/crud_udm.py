# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH
from __future__ import annotations

import builtins
from typing import Any, Generic, TypeVar

from loguru import logger
from scim2_models import Group, Resource, User
from univention.scim.server.domain.crud_scim import CrudScim


T = TypeVar("T", bound=Resource)


class CrudUdm(Generic[T], CrudScim[T]):
    """
    Implementation of CrudScim that uses UDM (Univention Directory Manager)
    for CRUD operations on resources.
    """

    def __init__(self, resource_type: str, scim2udm_mapper: Any, udm2scim_mapper: Any, resource_class: type[T]):
        """
        Initialize the UDM CRUD implementation.
        Args:
            resource_type: The type of resource ('User' or 'Group')
            scim2udm_mapper: Mapper to convert SCIM objects to UDM
            udm2scim_mapper: Mapper to convert UDM to SCIM objects
            resource_class: The class of resource being managed (e.g., User, Group)
        """
        self.resource_type = resource_type
        self.resource_class = resource_class
        self.scim2udm_mapper = scim2udm_mapper
        self.udm2scim_mapper = udm2scim_mapper
        self.udm_module = f"users/{resource_type.lower()}"
        self.logger = logger.bind(resource_type=resource_type)
        self.logger.info("Initialized UDM CRUD.")

    async def get(self, resource_id: str) -> T:
        """
        Get a resource by ID.
        Args:
            resource_id: The resource's unique identifier
        Returns:
            The resource if found
        Raises:
            ValueError: If the resource is not found
        """
        self.logger.trace("Getting resource from UDM", id=resource_id)

        # Here would be UDM API calls to get the object
        # For now, we'll simulate it
        if not resource_id:
            raise ValueError(f"Invalid {self.resource_type} ID: {resource_id}")

        # This would be replaced with actual UDM lookup
        # udm_obj = await self._get_udm_object(resource_id)

        # Convert UDM object to SCIM resource
        # scim_resource = self.udm2scim_mapper.to_scim(udm_obj)

        # For demonstration, create a mock object
        scim_resource: T
        if self.resource_class == User:
            scim_resource = User(id=resource_id, user_name=f"user_{resource_id}", display_name=f"User {resource_id}")
        elif self.resource_class == Group:
            scim_resource = Group(id=resource_id, display_name=f"Group {resource_id}")
        else:
            raise ValueError(f"Unsupported resource class: {self.resource_class}")

        return scim_resource

    async def list(
        self, filter_str: str | None = None, start_index: int = 1, count: int | None = None
    ) -> builtins.list[T]:
        """
        List resources with optional filtering and pagination.
        Args:
            filter_str: SCIM filter expression
            start_index: 1-based index for the first result
            count: Maximum number of results to return
        Returns:
            List of resources
        """
        self.logger.trace("Listing resources using UDM.", filter_str=filter_str)

        # Here would be UDM API calls to list objects with filtering
        # For now, we'll simulate it

        # Convert UDM filter to UDM query
        # udm_filter = self.scim2udm_mapper.to_udm_filter(filter_str)

        # Get objects from UDM
        # udm_objects = await self._list_udm_objects(udm_filter, start_index - 1, count)

        # Convert UDM objects to SCIM resources
        # scim_resources = [self.udm2scim_mapper.to_scim(obj) for obj in udm_objects]

        # For demonstration, return mock objects
        results = []
        for i in range(start_index, (start_index + (count or 10))):
            if self.resource_class == User:
                resource = User(id=f"mock-id-{i}", user_name=f"user_{i}", display_name=f"User {i}")
            elif self.resource_class == Group:
                resource = Group(id=f"mock-id-{i}", display_name=f"Group {i}")
            else:
                continue

            results.append(resource)

        return results

    async def count(self, filter_str: str | None = None) -> int:
        """
        Count resources matching a filter.
        Args:
            filter_str: SCIM filter expression
        Returns:
            Number of matching resources
        """
        self.logger.trace("Counting resources in UDM", filter_str=filter_str)

        # Here would be UDM API calls to count objects
        # For now, we'll simulate it

        # Convert SCIM filter to UDM filter
        # udm_filter = self.scim2udm_mapper.to_udm_filter(filter_str)

        # Count objects in UDM
        # count = await self._count_udm_objects(udm_filter)

        # For demonstration, return mock count
        return 42

    async def create(self, resource: T) -> T:
        """
        Create a new resource.
        Args:
            resource: The resource to create
        Returns:
            The created resource with server-assigned attributes
        """
        self.logger.trace("Creating resource in UDM")

        # Here would be UDM API calls to create object
        # For now, we'll simulate it

        # Convert SCIM resource to UDM properties
        # udm_props = self.scim2udm_mapper.to_udm(resource)

        # Create object in UDM
        # udm_obj = await self._create_udm_object(udm_props)

        # Convert UDM object back to SCIM resource
        # created_resource = self.udm2scim_mapper.to_scim(udm_obj)

        # For demonstration, return the resource with additional attributes
        if not resource.id:
            import uuid

            resource.id = str(uuid.uuid4())

        # Add server-assigned metadata
        resource.meta = {
            "resource_type": self.resource_type,
            "created": "2025-01-01T00:00:00Z",
            "last_modified": "2025-01-01T00:00:00Z",
            "version": 'W/"1"',
        }

        return resource

    async def update(self, resource_id: str, resource: T) -> T:
        """
        Update an existing resource.
        Args:
            resource_id: The resource's unique identifier
            resource: The updated resource data
        Returns:
            The updated resource
        Raises:
            ValueError: If the resource is not found
        """
        self.logger.trace("Updating resource using UDM", id=resource_id)

        # Here would be UDM API calls to update object
        # For now, we'll simulate it

        # Get existing UDM object
        # udm_obj = await self._get_udm_object(resource_id)
        # if not udm_obj:
        #     raise ValueError(f"{self.resource_type} with ID {resource_id} not found")

        # Convert SCIM resource to UDM properties
        # udm_props = self.scim2udm_mapper.to_udm(resource)

        # Update object in UDM
        # updated_obj = await self._update_udm_object(resource_id, udm_props)

        # Convert UDM object back to SCIM resource
        # updated_resource = self.udm2scim_mapper.to_scim(updated_obj)

        # For demonstration, return the resource with updated metadata
        resource.meta = {
            "resource_type": self.resource_type,
            "created": "2025-01-01T00:00:00Z",
            "last_modified": "2025-01-01T01:00:00Z",
            "version": 'W/"2"',
        }

        return resource

    async def delete(self, resource_id: str) -> bool:
        """
        Delete a resource.
        Args:
            resource_id: The resource's unique identifier
        Returns:
            True if the resource was deleted
        Raises:
            ValueError: If the resource is not found
        """
        self.logger.debug("Deleting resource from UDM", id=resource_id)

        # Here would be UDM API calls to delete object
        # For now, we'll simulate it

        # Delete object in UDM
        # success = await self._delete_udm_object(resource_id)

        # For demonstration, return success
        return True
