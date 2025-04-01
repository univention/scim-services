# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH
from loguru import logger
from scim2_models import Group, ResourceType, Schema, ServiceProviderConfig, User
from univention.scim.server.model_service.load_schemas import LoadSchemas


class LoadSchemasImpl(LoadSchemas):
    """
    Implementation of schema loading service.

    Provides default SCIM schemas and resource types.
    """

    async def get_user_schema(self) -> Schema:
        """Get the User schema."""
        logger.debug("Loading User schema")
        return User.to_schema()

    async def get_group_schema(self) -> Schema:
        """Get the Group schema."""
        logger.debug("Loading Group schema")
        return Group.to_schema()

    async def get_service_provider_config_schema(self) -> Schema:
        """Get the ServiceProviderConfig schema."""
        logger.debug("Loading ServiceProviderConfig schema")
        return ServiceProviderConfig.to_schema()

    async def get_resource_types(self) -> list[ResourceType]:
        """Get the available resource types."""
        logger.debug("Loading resource types")

        user_type = ResourceType.from_resource(User)
        group_type = ResourceType.from_resource(Group)

        return [user_type, group_type]
