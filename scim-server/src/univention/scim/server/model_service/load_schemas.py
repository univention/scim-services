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
    def get_supported_schemas(self) -> list[Schema]:
        """
        Get all supported schema.

        Returns:
            List of supported SCIM schemas
        """
        pass

    @abstractmethod
    def get_resource_types(self) -> list[ResourceType]:
        """
        Get the available resource types.

        Returns:
            List of SCIM ResourceType objects
        """
        pass
