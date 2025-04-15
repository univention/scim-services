# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

from abc import ABC, abstractmethod

from scim2_models import ResourceType, Schema


class LoadSchemas(ABC):
    """
    Interface for schema loading services.

    Defines methods for retrieving SCIM schemas and resource types.
    """

    @abstractmethod
    async def get_user_schema(self) -> Schema:
        """
        Get the User schema.

        Returns:
            The SCIM User schema
        """
        pass

    @abstractmethod
    async def get_group_schema(self) -> Schema:
        """
        Get the Group schema.

        Returns:
            The SCIM Group schema
        """
        pass

    @abstractmethod
    async def get_service_provider_config_schema(self) -> Schema:
        """
        Get the ServiceProviderConfig schema.

        Returns:
            The SCIM ServiceProviderConfig schema
        """
        pass

    @abstractmethod
    async def get_resource_types(self) -> list[ResourceType]:
        """
        Get the available resource types.

        Returns:
            List of SCIM ResourceType objects
        """
        pass
