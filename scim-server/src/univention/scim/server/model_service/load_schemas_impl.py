# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

from loguru import logger
from scim2_models import (
    EnterpriseUser,
    Group,
    ResourceType,
    Schema,
    SchemaExtension,
    ServiceProviderConfig,
    User,
)

from univention.scim.server.model_service.load_schemas import LoadSchemas
from univention.scim.server.models.extensions.customer1_user import Customer1User
from univention.scim.server.models.extensions.univention_group import UniventionGroup
from univention.scim.server.models.extensions.univention_user import UniventionUser


class LoadSchemasImpl(LoadSchemas):
    """
    Implementation of schema loading service.

    Provides default SCIM schemas and resource types.
    """

    def _get_user_schema(self) -> Schema:
        """Get the User schema."""
        # scim2-models does not add parent members to schema so patch schema on our own
        logger.debug("Loading User schema")
        user_schema = User.to_schema()

        # UDM requires a last name so adapt our schema accordingly
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
        # scim2-models does not add parent members to schema so patch schema on our own
        logger.debug("Loading Group schema")
        group_schema = Group.to_schema()

        # UDM requires a name so adapt our schema accordingly
        display_name_attribute = next(x for x in group_schema.attributes if x.name == "displayName")
        display_name_attribute.required = True

        return group_schema

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

        user_type = ResourceType.from_resource(User)
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
