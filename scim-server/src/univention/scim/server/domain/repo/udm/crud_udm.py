# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

from __future__ import annotations

import builtins
from typing import Any, Generic, TypeVar, cast

from loguru import logger
from scim2_models import Group, Resource, User
from univention.admin.rest.client import UDM

from univention.scim.server.domain.crud_scim import CrudScim


T = TypeVar("T", bound=Resource)


class CrudUdm(Generic[T], CrudScim[T]):
    """
    Implementation of CrudScim that uses UDM (Univention Directory Manager)
    REST API client for CRUD operations on resources.
    """

    def __init__(
        self,
        resource_type: str,
        scim2udm_mapper: Any,
        udm2scim_mapper: Any,
        resource_class: type[T],
        udm_url: str,
        udm_username: str,
        udm_password: str,
    ):
        """
        Initialize the UDM CRUD implementation.
        Args:
            resource_type: The type of resource ('User' or 'Group')
            scim2udm_mapper: Mapper to convert SCIM objects to UDM
            udm2scim_mapper: Mapper to convert UDM to SCIM objects
            resource_class: The class of resource being managed (e.g., User, Group)
            udm_url: URL of the UDM REST API
            udm_username: Username for UDM authentication
            udm_password: Password for UDM authentication
        """
        self.resource_type = resource_type
        self.resource_class = resource_class
        self.scim2udm_mapper = scim2udm_mapper
        self.udm2scim_mapper = udm2scim_mapper
        self.udm_module_name = "users/user" if resource_class == User else "groups/group"

        # UDM REST API configuration
        self.udm_url = udm_url.rstrip("/")
        self.udm_username = udm_username
        self.udm_password = udm_password

        # Initialize UDM client
        self.udm_client = UDM.http(f"{self.udm_url}/", self.udm_username, self.udm_password)

        self.logger = logger.bind(resource_type=resource_type)
        self.logger.info("Initialized UDM CRUD with UDM REST API client")

    async def get(self, resource_id: str) -> T:
        """
        Get a resource by ID.
        Args:
            resource_id: The resource's unique identifier (univentionObjectIdentifier)
        Returns:
            The resource if found
        Raises:
            ValueError: If the resource is not found
        """
        self.logger.trace("Getting resource from UDM", id=resource_id)

        if not resource_id:
            raise ValueError(f"Invalid {self.resource_type} ID: {resource_id}")

        try:
            # Get the module
            module = self.udm_client.get(self.udm_module_name)

            # Construct filter for UDM REST API to find by univentionObjectIdentifier
            filter_str = f"univentionObjectIdentifier={resource_id}"

            # Search for the object
            results = list(module.search(filter_str))

            if not results:
                raise ValueError(f"{self.resource_type} with ID {resource_id} not found")

            # Get the first matching object (should be only one)
            udm_obj = results[0].open()

            # Convert UDM object to SCIM resource
            if self.resource_class == User:
                scim_resource = self.udm2scim_mapper.map_user(udm_obj, base_url=self.udm_url)
            elif self.resource_class == Group:
                scim_resource = self.udm2scim_mapper.map_group(udm_obj, base_url=self.udm_url)
            else:
                raise ValueError(f"Unsupported resource class: {self.resource_class}")

            return cast(T, scim_resource)

        except Exception as e:
            self.logger.error(f"Error retrieving {self.resource_type}: {e}")
            raise ValueError(f"Error retrieving {self.resource_type}: {str(e)}") from e

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

        # Convert SCIM filter to UDM filter if provided
        udm_filter = self._convert_scim_filter_to_udm(filter_str) if filter_str else None

        try:
            # Get the module
            module = self.udm_client.get(self.udm_module_name)

            # Set pagination parameters
            # UDM uses index-based pagination (start from 0), so we need to convert from 1-based
            offset = start_index - 1 if start_index > 1 else 0
            limit = count if count else None

            # Search for objects
            results = list(
                module.search(
                    udm_filter,
                    position=None,  # Search everywhere
                    scope="sub",  # Subtree search
                    hidden=False,  # Don't include hidden objects
                    offset=offset,
                    limit=limit,
                )
            )

            # Convert UDM objects to SCIM resources
            resources: builtins.list[T] = []
            for result in results:
                udm_obj = result.open()
                if self.resource_class == User:
                    resource = self.udm2scim_mapper.map_user(udm_obj, base_url=self.udm_url)
                elif self.resource_class == Group:
                    resource = self.udm2scim_mapper.map_group(udm_obj, base_url=self.udm_url)
                else:
                    continue

                resources.append(cast(T, resource))

            return resources

        except Exception as e:
            self.logger.error(f"Error listing {self.resource_type}s: {e}")
            raise ValueError(f"Error listing {self.resource_type}s: {str(e)}") from e

    async def count(self, filter_str: str | None = None) -> int:
        """
        Count resources matching a filter.
        Args:
            filter_str: SCIM filter expression
        Returns:
            Number of matching resources
        """
        self.logger.trace("Counting resources in UDM", filter_str=filter_str)

        # Convert SCIM filter to UDM filter if provided
        udm_filter = self._convert_scim_filter_to_udm(filter_str) if filter_str else None

        try:
            # Get the module
            module = self.udm_client.get(self.udm_module_name)

            # Count the objects by fetching them (UDM client doesn't have a dedicated count method)
            results = list(
                module.search(
                    udm_filter,
                    position=None,  # Search everywhere
                    scope="sub",  # Subtree search
                    hidden=False,  # Don't include hidden objects
                )
            )

            return len(results)

        except Exception as e:
            self.logger.error(f"Error counting {self.resource_type}s: {e}")
            raise ValueError(f"Error counting {self.resource_type}s: {str(e)}") from e

    async def create(self, resource: T) -> T:
        """
        Create a new resource.
        Args:
            resource: The resource to create
        Returns:
            The created resource with server-assigned attributes
        """
        self.logger.trace("Creating resource in UDM")

        try:
            # Get the module
            module = self.udm_client.get(self.udm_module_name)

            # Create a new object
            udm_obj = module.new()

            # Convert SCIM resource to UDM properties
            if self.resource_class == User:
                self.scim2udm_mapper.map_user(resource, udm_obj)
            elif self.resource_class == Group:
                self.scim2udm_mapper.map_group(resource, udm_obj)
            else:
                raise ValueError(f"Unsupported resource class: {self.resource_class}")

            # Save the object
            udm_obj.save()

            # Convert the saved UDM object back to SCIM resource
            if self.resource_class == User:
                created_resource = self.udm2scim_mapper.map_user(udm_obj, base_url=self.udm_url)
            elif self.resource_class == Group:
                created_resource = self.udm2scim_mapper.map_group(udm_obj, base_url=self.udm_url)
            else:
                raise ValueError(f"Unsupported resource class: {self.resource_class}")

            return cast(T, created_resource)

        except Exception as e:
            self.logger.error(f"Error creating {self.resource_type}: {e}")
            raise ValueError(f"Error creating {self.resource_type}: {str(e)}") from e

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
        self.logger.trace("Updating resource in UDM", id=resource_id)

        try:
            # First retrieve the existing object
            await self.get(resource_id)

            # Get the module
            module = self.udm_client.get(self.udm_module_name)

            # Construct filter for UDM REST API to find by univentionObjectIdentifier
            filter_str = f"univentionObjectIdentifier={resource_id}"

            # Get the object
            results = list(module.search(filter_str))

            if not results:
                raise ValueError(f"{self.resource_type} with ID {resource_id} not found")

            # Get the first matching object (should be only one)
            udm_obj = results[0].open()

            # Update the UDM object with the new resource data
            if self.resource_class == User:
                self.scim2udm_mapper.map_user(resource, udm_obj)
            elif self.resource_class == Group:
                self.scim2udm_mapper.map_group(resource, udm_obj)
            else:
                raise ValueError(f"Unsupported resource class: {self.resource_class}")

            # Save the updated object
            udm_obj.save()

            # Convert the saved UDM object back to SCIM resource
            if self.resource_class == User:
                updated_resource = self.udm2scim_mapper.map_user(udm_obj, base_url=self.udm_url)
            elif self.resource_class == Group:
                updated_resource = self.udm2scim_mapper.map_group(udm_obj, base_url=self.udm_url)
            else:
                raise ValueError(f"Unsupported resource class: {self.resource_class}")

            return cast(T, updated_resource)

        except Exception as e:
            self.logger.error(f"Error updating {self.resource_type}: {e}")
            raise ValueError(f"Error updating {self.resource_type}: {str(e)}") from e

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
        self.logger.trace("Deleting resource from UDM", id=resource_id)

        try:
            # Get the module
            module = self.udm_client.get(self.udm_module_name)

            # Construct filter for UDM REST API to find by univentionObjectIdentifier
            filter_str = f"univentionObjectIdentifier={resource_id}"

            # Search for the object
            results = list(module.search(filter_str))

            if not results:
                raise ValueError(f"{self.resource_type} with ID {resource_id} not found")

            # Get the first matching object (should be only one)
            udm_obj = results[0].open()

            # Delete the object
            udm_obj.delete()

            return True

        except Exception as e:
            self.logger.error(f"Error deleting {self.resource_type}: {e}")
            raise ValueError(f"Error deleting {self.resource_type}: {str(e)}") from e

    def _convert_scim_filter_to_udm(self, scim_filter: str) -> str:
        """
        Convert a SCIM filter to a UDM filter.
        This is a simplified implementation that handles basic univentionObjectIdentifier filtering.

        Args:
            scim_filter: SCIM filter expression
        Returns:
            UDM filter expression
        """
        # Very basic conversion for the univentionObjectIdentifier filter
        # A proper implementation would need a more sophisticated parser
        if "id eq " in scim_filter:
            # Extract the ID value
            id_value = scim_filter.split("id eq ")[1].strip("\"'")
            return f"univentionObjectIdentifier={id_value}"

        # Handle userName filter for users
        if "userName eq " in scim_filter and self.resource_class == User:
            username = scim_filter.split("userName eq ")[1].strip("\"'")
            return f"username={username}"

        # Handle displayName filter for groups
        if "displayName eq " in scim_filter and self.resource_class == Group:
            displayname = scim_filter.split("displayName eq ")[1].strip("\"'")
            return f"name={displayname}"

        # Pass through other filters as-is (would need proper conversion in production)
        return scim_filter
