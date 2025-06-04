# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

from typing import TypeAlias

from loguru import logger
from scim2_models import EnterpriseUser, Group, Meta, ResourceType, Schema, SchemaExtension, ServiceProviderConfig, User

from univention.scim.server.config import ApplicationSettings
from univention.scim.server.model_service.load_schemas import LoadSchemas


UserWithExtensions: TypeAlias = User[EnterpriseUser]
GroupWithExtensions: TypeAlias = Group


class LoadSchemasImpl(LoadSchemas):
    """
    Implementation of schema loading service.

    Provides default SCIM schemas and resource types.
    """

    def __init__(self, settings: ApplicationSettings) -> None:
        self.base_url = f"{settings.host}{settings.api_prefix}"

    def _get_user_schema(self) -> Schema:
        """Get the User schema."""
        logger.debug("Loading User schema")
        user_schema = User.to_schema()
        # UDM requires a last name so adept our schema accordingly
        name_attribute = next(x for x in user_schema.attributes if x.name == "name")
        name_attribute.required = True
        family_name_sub_attribute = next(x for x in name_attribute.sub_attributes if x.name == "familyName")
        family_name_sub_attribute.required = True

        return user_schema

    def _get_user_extension_schemas(self) -> list[Schema]:
        user_extensions = [EnterpriseUser.to_schema()]

        return user_extensions

    def _get_group_schema(self) -> Schema:
        """Get the Group schema."""
        logger.debug("Loading Group schema")
        return Group.to_schema()

    def _get_group_extension_schemas(self) -> list[Schema]:
        return []

    def _get_service_provider_config_schema(self) -> Schema:
        """Get the ServiceProviderConfig schema."""
        logger.debug("Loading ServiceProviderConfig schema")
        return ServiceProviderConfig.to_schema()

    def get_supported_schemas(self) -> list[Schema]:
        return [
            self._get_user_schema(),
            *self._get_user_extension_schemas(),
            self._get_group_schema(),
            *self._get_group_extension_schemas(),
            self._get_service_provider_config_schema(),
        ]

    def get_resource_types(self) -> list[ResourceType]:
        """Get the available resource types."""
        logger.debug("Loading resource types")

        user_type = ResourceType.from_resource(User)
        for extension in self._get_user_extension_schemas():
            user_type.schema_extensions.append(
                SchemaExtension(
                    schema_=extension.id,
                    required=False,
                )
            )
        user_type.meta = Meta(location=f"{self.base_url}/ResourceTypes/User", resourceType="ResourceType")

        group_type = ResourceType.from_resource(Group)
        for extension in self._get_group_extension_schemas():
            user_type.schema_extensions.append(
                SchemaExtension(
                    schema_=extension.id,
                    required=False,
                )
            )
        group_type.meta = Meta(location=f"{self.base_url}/ResourceTypes/Group", resourceType="ResourceType")

        return [user_type, group_type]
