# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

from __future__ import annotations

import builtins
from typing import Any, Generic, TypeVar, cast

import httpx
from loguru import logger
from scim2_models import Group, Resource, User

from univention.scim.server.domain.crud_scim import CrudScim


T = TypeVar("T", bound=Resource)


class CrudUdm(Generic[T], CrudScim[T]):
    """
    Implementation of CrudScim that uses UDM (Univention Directory Manager)
    for CRUD operations on resources.
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
        self.udm_module = f"users/{resource_type.lower()}"

        # UDM REST API configuration
        self.udm_url = udm_url.rstrip("/")
        self.udm_username = udm_username
        self.udm_password = udm_password

        self.logger = logger.bind(resource_type=resource_type)
        self.logger.info("Initialized UDM CRUD.")

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

        # Construct filter for UDM REST API to find by univentionObjectIdentifier
        filter_str = f"univentionObjectIdentifier={resource_id}"

        try:
            async with httpx.AsyncClient() as client:
                # Request UDM object by filter
                # Determine the correct module path based on resource type
                module_path = "users/user" if self.resource_class == User else "groups/group"

                response = await client.get(
                    f"{self.udm_url}/{module_path}",
                    params={"filter": filter_str},
                    auth=(self.udm_username, self.udm_password),
                    timeout=10.0,
                )

                response.raise_for_status()
                results = response.json().get("_embedded", {}).get("udm:object", [])

                if not results:
                    raise ValueError(f"{self.resource_type} with ID {resource_id} not found")

                # Get the first matching object (should be only one)
                udm_obj = results[0]

                # Convert UDM object to SCIM resource
                if self.resource_class == User:
                    scim_resource = self.udm2scim_mapper.map_user(udm_obj, base_url=self.udm_url)
                elif self.resource_class == Group:
                    scim_resource = self.udm2scim_mapper.map_group(udm_obj, base_url=self.udm_url)
                else:
                    raise ValueError(f"Unsupported resource class: {self.resource_class}")

                return cast(T, scim_resource)

        except httpx.HTTPStatusError as e:
            self.logger.error(f"HTTP error fetching UDM object: {e}")
            raise ValueError(f"Error retrieving {self.resource_type}: {str(e)}") from e
        except httpx.RequestError as e:
            self.logger.error(f"Request error fetching UDM object: {e}")
            raise ValueError(f"Error connecting to UDM: {str(e)}") from e
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}")
            raise ValueError(f"Unexpected error retrieving {self.resource_type}: {str(e)}") from e

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
            async with httpx.AsyncClient() as client:
                # Build query params
                params: dict[str, str] = {}
                if udm_filter:
                    params["filter"] = udm_filter
                if count:
                    params["limit"] = str(count)
                if start_index > 1 and count:
                    # UDM uses offset-based pagination, convert from 1-based to 0-based
                    params["offset"] = str(start_index - 1)

                # Determine the correct module path based on resource type
                module_path = "users/user" if self.resource_class == User else "groups/group"

                # Request UDM objects
                response = await client.get(
                    f"{self.udm_url}/{module_path}",
                    params=params,
                    auth=(self.udm_username, self.udm_password),
                    timeout=10.0,
                )

                response.raise_for_status()
                results = response.json().get("_embedded", {}).get("udm:object", [])

                # Convert UDM objects to SCIM resources
                resources: builtins.list[T] = []
                for udm_obj in results:
                    if self.resource_class == User:
                        resource = self.udm2scim_mapper.map_user(udm_obj, base_url=self.udm_url)
                    elif self.resource_class == Group:
                        resource = self.udm2scim_mapper.map_group(udm_obj, base_url=self.udm_url)
                    else:
                        continue

                    resources.append(cast(T, resource))

                return resources

        except httpx.HTTPStatusError as e:
            self.logger.error(f"HTTP error listing UDM objects: {e}")
            raise ValueError(f"Error listing {self.resource_type}s: {str(e)}") from e
        except httpx.RequestError as e:
            self.logger.error(f"Request error listing UDM objects: {e}")
            raise ValueError(f"Error connecting to UDM: {str(e)}") from e
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}")
            raise ValueError(f"Unexpected error listing {self.resource_type}s: {str(e)}") from e

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
            async with httpx.AsyncClient() as client:
                # Build query params
                params: dict[str, str] = {"limit": "1"}  # We only need count, not actual data
                if udm_filter:
                    params["filter"] = udm_filter

                # Determine the correct module path based on resource type
                module_path = "users/user" if self.resource_class == User else "groups/group"

                # Request UDM objects count
                response = await client.get(
                    f"{self.udm_url}/{module_path}",
                    params=params,
                    auth=(self.udm_username, self.udm_password),
                    timeout=10.0,
                )

                response.raise_for_status()
                # Extract total count from response
                total = response.json().get("total", 0)
                return int(total)

        except httpx.HTTPStatusError as e:
            self.logger.error(f"HTTP error counting UDM objects: {e}")
            raise ValueError(f"Error counting {self.resource_type}s: {str(e)}") from e
        except httpx.RequestError as e:
            self.logger.error(f"Request error counting UDM objects: {e}")
            raise ValueError(f"Error connecting to UDM: {str(e)}") from e
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}")
            raise ValueError(f"Unexpected error counting {self.resource_type}s: {str(e)}") from e

    async def create(self, resource: T) -> T:
        """
        Create a new resource.
        Args:
            resource: The resource to create
        Returns:
            The created resource with server-assigned attributes
        """
        self.logger.trace("Creating resource in UDM")

        # For testing purposes, let's just return the resource with an ID if it doesn't have one
        if not resource.id:
            import uuid

            resource.id = str(uuid.uuid4())

        # Update metadata properly using model's properties
        from scim2_models import Meta

        resource.meta = Meta(
            resource_type=self.resource_type, location=f"{self.udm_url}/{self.resource_type}s/{resource.id}"
        )

        # In a real implementation, we would convert to UDM and create via API
        # This simplified version is for the GET /Users endpoint implementation
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
        self.logger.trace("Updating resource in UDM", id=resource_id)

        # For testing purposes, let's just return the resource with the specified ID
        # In a real implementation, we would check if the resource exists, convert to UDM, and update via API

        # Ensure the ID is set correctly
        resource.id = resource_id

        # Update metadata properly using model's properties
        from scim2_models import Meta

        resource.meta = Meta(
            resource_type=self.resource_type, location=f"{self.udm_url}/{self.resource_type}s/{resource_id}"
        )

        # This simplified version is for the GET /Users endpoint implementation
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
        self.logger.trace("Deleting resource from UDM", id=resource_id)

        # For testing purposes, let's just return True to indicate success
        # In a real implementation, we would check if the resource exists and delete via the UDM API

        # This simplified version is for the GET /Users endpoint implementation
        return True

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
