# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

from typing import Any, Generic, TypeVar, cast

from asgi_correlation_id import correlation_id as asgi_correlation_id  # Added for accessing upstream correlation ID
from loguru import logger
from scim2_models import Group, Resource, User
from univention.admin.rest.client import UDM, Object

from univention.scim.server.domain.crud_scim import CrudScim
from univention.scim.transformation.exceptions import MappingError


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
        udm_client: UDM,
        base_url: str,
        external_id_mapping: str | None = None,
    ):
        """
        Initialize the UDM CRUD implementation.
        Args:
            resource_type: The type of resource ('User' or 'Group')
            scim2udm_mapper: Mapper to convert SCIM objects to UDM
            udm2scim_mapper: Mapper to convert UDM to SCIM objects
            resource_class: The class of resource being managed (e.g., User, Group)
            udm_client: UDM REST API client
            base_url: Base URL used for SCIM resource location
            external_id_mapping: UDM property to map to SCIM externalId (optional)
        """
        self.resource_type = resource_type
        self.resource_class = resource_class
        self.scim2udm_mapper = scim2udm_mapper
        self.udm2scim_mapper = udm2scim_mapper
        self.udm_module_name = "users/user" if resource_class == User else "groups/group"
        self.external_id_mapping = external_id_mapping

        self.base_url = base_url.rstrip("/")

        self.udm_client = udm_client

        self.logger = logger.bind(resource_type=resource_type)
        self.logger.info("Initialized UDM CRUD with UDM REST API client", external_id_mapping=external_id_mapping)

    def _generate_udm_request_id(self) -> str:
        """
        Returns the upstream correlation ID for UDM requests to maintain
        the same correlation ID throughout the request chain.
        """
        upstream_correlation_id: str = str(asgi_correlation_id.get())
        self.logger.bind(
            correlation_id=upstream_correlation_id,
        ).debug("Using upstream correlation ID for UDM request.")
        return upstream_correlation_id

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
            return self._convert_object_to_scim(udm_obj)

        except Exception as e:
            self.logger.error(f"Error retrieving {self.resource_type}: {e}")
            raise ValueError(f"Error retrieving {self.resource_type}: {str(e)}") from e

    async def list(
        self, filter_str: str | None = None, start_index: int = 1, count: int | None = None
    ) -> tuple[int, list[T]]:
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
            results = module.search(
                udm_filter,
                position=None,  # Search everywhere
                scope="sub",  # Subtree search
                hidden=False,  # Don't include hidden objects
            )

            # Convert UDM objects to SCIM resources
            resources: list[T] = []
            end_pos = offset + limit if limit else None
            total_results = 0
            valid_objects = 0
            for result in results:
                udm_obj = result.open()

                try:
                    resource = self._convert_object_to_scim(udm_obj)
                except ValueError:
                    continue

                if valid_objects >= offset and (not end_pos or valid_objects < end_pos):
                    # might be different if pagination is implemented:
                    #  - resources: only contains the values on one page
                    #  - total_results: all available results based on the request
                    total_results += 1
                    resources.append(resource)

                valid_objects += 1

            return total_results, resources

        except Exception as e:
            self.logger.error(f"Error listing {self.resource_type}s: {e}")
            raise ValueError(f"Error listing {self.resource_type}s: {str(e)}") from e

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

            properties: dict[str, Any]

            # Convert SCIM resource to UDM properties
            if self.resource_class == User:
                properties = self.scim2udm_mapper.map_user(resource)

                if resource.ignore_password_policy:
                    self.logger.debug("Ignore password policy and history")
                    properties["overridePWHistory"] = True
                    properties["overridePWLength"] = True

            elif self.resource_class == Group:
                properties = self.scim2udm_mapper.map_group(resource)
            else:
                raise ValueError(f"Unsupported resource class: {self.resource_class}")

            for key, value in properties.items():
                udm_obj.properties[key] = value

            # Save the object
            udm_obj.save()

            # Convert the saved UDM object back to SCIM resource
            return self._convert_object_to_scim(udm_obj)

        except MappingError as e:
            self.logger.error(f"Error creating {self.resource_type}: {e}")
            raise e
        except Exception as e:
            self.logger.error(f"Error creating {self.resource_type}: {e}")
            raise ValueError(f"Error creating {self.resource_type}: {str(e)}") from e

    async def update(self, resource_id: str, resource: T) -> T:
        """
        Update an existing resource using PUT semantics (full replacement).
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

            # Ensure the resource has the correct ID
            if not resource.id:
                resource.id = resource_id
            elif resource.id != resource_id:
                raise ValueError(f"Resource ID mismatch: {resource.id} != {resource_id}")

            # Convert SCIM resource to UDM properties
            properties: dict[str, Any]

            if self.resource_class == User:
                properties = self.scim2udm_mapper.map_user(resource)
            elif self.resource_class == Group:
                properties = self.scim2udm_mapper.map_group(resource)
            else:
                raise ValueError(f"Unsupported resource class: {self.resource_class}")

            # Update UDM object properties
            for key, value in properties.items():
                udm_obj.properties[key] = value

            # Save the updated object
            udm_obj.save()

            # Convert the saved UDM object back to SCIM resource
            return self._convert_object_to_scim(udm_obj)

        except MappingError as e:
            self.logger.error(f"Error updating {self.resource_type}: {e}")
            raise e
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

    def _convert_object_to_scim(self, obj: Object) -> T:
        # Convert the saved UDM object back to SCIM resource
        if self.resource_class == User:
            try:
                return cast(T, self.udm2scim_mapper.map_user(obj, base_url=self.base_url))
            except ValueError:
                logger.error("Failed to map object, ignoring it")
                raise
        elif self.resource_class == Group:
            try:
                return cast(T, self.udm2scim_mapper.map_group(obj, base_url=self.base_url))
            except ValueError:
                logger.error("Failed to map object, ignoring it")
                raise
        else:
            raise ValueError(f"Unsupported resource class: {self.resource_class}")

    def _convert_scim_filter_to_udm(self, scim_filter: str) -> str | None:
        """
        Convert a SCIM filter to a UDM filter.
        This is a simplified implementation that handles basic filtering.

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

        # Handle externalId filter using configured mapping
        if "externalId eq " in scim_filter:
            external_id_value = scim_filter.split("externalId eq ")[1].strip("\"'")
            if self.external_id_mapping:
                self.logger.trace(
                    "Converting externalId filter", udm_property=self.external_id_mapping, value=external_id_value
                )
                return f"{self.external_id_mapping}={external_id_value}"
            else:
                self.logger.error("externalId filter requested but no mapping configured", filter={scim_filter})
                raise ValueError("externalId filter requested but no mapping configured")

        # Handle userName filter for users
        if "userName eq " in scim_filter and self.resource_class == User:
            username = scim_filter.split("userName eq ")[1].strip("\"'")
            return f"username={username}"

        # Handle displayName filter for groups
        if "displayName eq " in scim_filter and self.resource_class == Group:
            displayname = scim_filter.split("displayName eq ")[1].strip("\"'")
            if self.resource_class == User:
                return f"displayName={displayname}"
            if self.resource_class == Group:
                return f"name={displayname}"

        raise ValueError(
            "Filter query not supported yet. Filtering is only supported for: id, externalId, userName and displayName"
        )
