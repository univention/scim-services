# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

from typing import Annotated, Union

from loguru import logger
from pydantic import Field
from scim2_models import (
    AnyExtension,
    Email as ScimEmail,
    EnterpriseUser,
    Group,
    Name as ScimName,
    Required,
    ResourceType,
    Schema,
    SchemaExtension,
    ServiceProviderConfig,
    User as ScimUser,
)

from univention.scim.server.models.extensions.customer1_user import Customer1User
from univention.scim.server.model_service.extensions.univention_group import UniventionGroup
from univention.scim.server.model_service.extensions.univention_user import UniventionUser
from univention.scim.server.model_service.load_schemas import LoadSchemas


class LoadSchemasImpl(LoadSchemas):
    """
    Implementation of schema loading service.

    Provides default SCIM schemas and resource types.
    """

    def _get_user_schema(self) -> Schema:
        """Get the User schema."""
        # scim2-models does not add parent members to schema so patch schema on our own
        logger.debug("Loading User schema")
        user_schema = ScimUser.to_schema()

        # UDM requires a last name so adept our schema accordingly
        name_attribute = next(x for x in user_schema.attributes if x.name == "name")
        name_attribute.required = True
        family_name_sub_attribute = next(x for x in name_attribute.sub_attributes if x.name == "familyName")
        family_name_sub_attribute.required = True

        # Do not restrict the type of mails to allow mapping special UDM emails
        emails_attribute = next(x for x in user_schema.attributes if x.name == "emails")
        email_type_attribue = next(x for x in emails_attribute.sub_attributes if x.name == "type")
        email_type_attribue.canonical_values = None

        return user_schema

    def _get_group_schema(self) -> Schema:
        """Get the Group schema."""
        logger.debug("Loading Group schema")
        return Group.to_schema()

    def _get_user_extension_schemas(self) -> list[Schema]:
        user_extensions = [EnterpriseUser.to_schema(), UniventionUser.to_schema(), Customer1User.to_schema()]

        return user_extensions

    def _get_group_extension_schemas(self) -> list[Schema]:
        group_extensions = [UniventionGroup.to_schema()]

        return group_extensions

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

        user_type = ResourceType.from_resource(ScimUser)
        for extension in self._get_user_extension_schemas():
            user_type.schema_extensions.append(
                SchemaExtension(
                    schema_=extension.id,
                    required=False,
                )
            )

        group_type = ResourceType.from_resource(Group)
        for extension in self._get_group_extension_schemas():
            group_type.schema_extensions.append(
                SchemaExtension(
                    schema_=extension.id,
                    required=False,
                )
            )

        return [user_type, group_type]
