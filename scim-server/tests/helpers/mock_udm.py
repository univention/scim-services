# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH
import builtins
import uuid
from typing import Any, Generic, TypeVar

from loguru import logger
from scim2_models import Meta, Resource, User

from univention.scim.server.domain.crud_scim import CrudScim


T = TypeVar("T", bound=Resource)


class MockCrudUdm(Generic[T], CrudScim[T]):
    """
    In-memory UDM mock for testing purposes.
    Simulates a UDM backend without making actual HTTP calls.
    """

    def __init__(
        self,
        resource_type: str,
        scim2udm_mapper: Any,
        udm2scim_mapper: Any,
        resource_class: type[T],
        udm_url: str = "http://test.local",
        udm_username: str = "test",
        udm_password: str = "test",
    ):
        """
        Initialize the mock UDM CRUD implementation.
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
        self.udm_url = udm_url
        self.udm_username = udm_username
        self.udm_password = udm_password

        # In-memory storage
        self.resources: dict[str, T] = {}
        self.logger = logger.bind(resource_type=resource_type)
        self.logger.info("Initialized Mock UDM CRUD.")

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
        if resource_id not in self.resources:
            raise ValueError(f"{self.resource_type} with ID {resource_id} not found")
        return self.resources[resource_id]

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
        resources = list(self.resources.values())

        # Apply filtering (very simplified version)
        if filter_str:
            filtered_resources = []
            # Handle basic attribute filters (very simplified)
            if "id eq " in filter_str:
                id_value = filter_str.split("id eq ")[1].strip("\"'")
                filtered_resources = [r for r in resources if r.id == id_value]
            elif "userName eq " in filter_str:
                username = filter_str.split("userName eq ")[1].strip("\"'")
                filtered_resources = [r for r in resources if isinstance(r, User) and r.user_name == username]
            elif "displayName eq " in filter_str:
                displayname = filter_str.split("displayName eq ")[1].strip("\"'")
                filtered_resources = [
                    r for r in resources if hasattr(r, "display_name") and r.display_name == displayname
                ]
            else:
                # If filter not recognized, return all
                filtered_resources = resources
        else:
            filtered_resources = resources

        # Apply pagination
        if count is not None:
            end_index = start_index + count - 1 if count > 0 else len(filtered_resources)
            return filtered_resources[start_index - 1 : end_index]
        return filtered_resources

    async def count(self, filter_str: str | None = None) -> int:
        """
        Count resources matching a filter.
        Args:
            filter_str: SCIM filter expression
        Returns:
            Number of matching resources
        """
        resources = await self.list(filter_str)
        return len(resources)

    async def create(self, resource: T) -> T:
        """
        Create a new resource.
        Args:
            resource: The resource to create
        Returns:
            The created resource with server-assigned attributes
        """
        # Generate an ID if not provided
        if not resource.id:
            resource.id = str(uuid.uuid4())

        # Store the resource
        self.resources[resource.id] = resource

        # Add metadata
        if not resource.meta:
            resource.meta = Meta(
                resource_type=self.resource_type, location=f"{self.udm_url}/{self.resource_type}s/{resource.id}"
            )

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
        if resource_id not in self.resources:
            raise ValueError(f"{self.resource_type} with ID {resource_id} not found")

        # Ensure the ID doesn't change
        resource.id = resource_id

        # Update metadata
        if not resource.meta:
            resource.meta = Meta(
                resource_type=self.resource_type, location=f"{self.udm_url}/{self.resource_type}s/{resource.id}"
            )

        # Update the resource
        self.resources[resource_id] = resource

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
        if resource_id not in self.resources:
            raise ValueError(f"{self.resource_type} with ID {resource_id} not found")

        del self.resources[resource_id]
        return True
