# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH
from typing import Generic, TypeVar

from loguru import logger
from scim2_models import Resource
from univention.scim.server.domain.crud_scim import CrudScim
from univention.scim.server.model_service.scim2udm import ScimToUdmMapper
from univention.scim.server.model_service.udm2scim import UdmToScimMapper


T = TypeVar("T", bound=Resource)


class CrudUdm(Generic[T], CrudScim[T]):
    """
    UDM implementation of the CrudScim interface.

    This implementation uses UDM as the backend for storing SCIM resources.
    """

    def __init__(self, resource_type: str, scim2udm_mapper: ScimToUdmMapper, udm2scim_mapper: UdmToScimMapper):
        """
        Initialize the UDM repository.

        Args:
            resource_type: The SCIM resource type (e.g., 'User', 'Group')
            scim2udm_mapper: Mapper to convert SCIM resources to UDM objects
            udm2scim_mapper: Mapper to convert UDM objects to SCIM resources
        """
        self.resource_type = resource_type
        self.scim2udm_mapper = scim2udm_mapper
        self.udm2scim_mapper = udm2scim_mapper

    async def get(self, resource_id: str) -> T:
        """Get a resource by ID."""
        logger.debug(f"Getting {self.resource_type} with ID {resource_id} from UDM")

        try:
            # TODO: Implement actual UDM lookup
            # For now, just return None to indicate not found
            return None
        except Exception as e:
            logger.error(f"Error retrieving {self.resource_type} from UDM: {e}")
            raise

    async def list(self, filter_str: str = None, start_index: int = 1, count: int = None) -> list[T]:
        """List resources with optional filtering and pagination."""
        logger.debug(f"Listing {self.resource_type}s from UDM with filter: {filter_str}")

        try:
            # TODO: Implement actual UDM search
            # For now, just return an empty list
            return []
        except Exception as e:
            logger.error(f"Error listing {self.resource_type}s from UDM: {e}")
            raise

    async def count(self, filter_str: str = None) -> int:
        """Count resources matching a filter."""
        logger.debug(f"Counting {self.resource_type}s in UDM with filter: {filter_str}")

        try:
            # TODO: Implement actual UDM count
            # For now, just return 0
            return 0
        except Exception as e:
            logger.error(f"Error counting {self.resource_type}s in UDM: {e}")
            raise

    async def create(self, resource: T) -> T:
        """Create a new resource."""
        logger.debug(f"Creating {self.resource_type} in UDM")

        try:
            # TODO: Implement actual UDM creation
            # For now, just return the input resource
            return resource
        except Exception as e:
            logger.error(f"Error creating {self.resource_type} in UDM: {e}")
            raise

    async def update(self, resource_id: str, resource: T) -> T:
        """Update an existing resource."""
        logger.debug(f"Updating {self.resource_type} with ID {resource_id} in UDM")

        try:
            # TODO: Implement actual UDM update
            # For now, just return the input resource
            return resource
        except Exception as e:
            logger.error(f"Error updating {self.resource_type} in UDM: {e}")
            raise

    async def delete(self, resource_id: str) -> bool:
        """Delete a resource."""
        logger.debug(f"Deleting {self.resource_type} with ID {resource_id} from UDM")

        try:
            # TODO: Implement actual UDM deletion
            # For now, just return True to indicate success
            return True
        except Exception as e:
            logger.error(f"Error deleting {self.resource_type} from UDM: {e}")
            raise
