# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

import functools
import operator

from loguru import logger
from pydantic import ValidationError
from scim2_models import EnterpriseUser, Extension, Group, Resource
from univention.provisioning.models import Message

from univention.scim.client.group_membership_resolver import GroupMembershipLdapResolver
from univention.scim.client.helper import cust_pformat
from univention.scim.client.scim_client_settings import ScimConsumerSettings
from univention.scim.client.scim_http_client import ScimClient, ScimClientNoDataFoundException

# FIXME: Use the models from the server for now because the original models are to strict
#        For example with the email type.
#        In the future the mapper should not operate on pydantic models but just dictionaries
from univention.scim.server.models.extensions.customer1_user import Customer1User
from univention.scim.server.models.extensions.univention_user import UniventionUser
from univention.scim.server.models.user import User
from univention.scim.transformation.udm2scim import UdmToScimMapper


_USER_EXTENSIONS: tuple[type[Extension], ...] = (EnterpriseUser, UniventionUser, Customer1User)


def _drop_unadvertised_attributes(
    resource: Resource, resource_type: type[Resource], discovered_model: type[Resource]
) -> None:
    """
    Null out any attribute of `resource` (an instance of `resource_type`) that the server's
    discovered schema doesn't declare thus will be dropped.

    Matched by SCIM attribute name (each field's `serialization_alias`, e.g. "x509Certificates"),
    not by Python field name -- dynamically built models (via Resource.from_schema()) can pick a
    different Python identifier for the same SCIM attribute than our static classes do (e.g.
    x509_certificates vs. x_509_certificates)
    """
    supported_attribute_names = {field.serialization_alias for field in discovered_model.model_fields.values()}
    for name, field in resource_type.model_fields.items():
        if field.serialization_alias not in supported_attribute_names:
            try:
                setattr(resource, name, None)
            except ValidationError:
                logger.debug(
                    "Cannot unset non-optional attribute {} not advertised by server", field.serialization_alias
                )


class ScimConsumer:
    """ """

    def __init__(
        self,
        scim_http_client: ScimClient,
        group_membership_resolver: GroupMembershipLdapResolver,
        settings: ScimConsumerSettings,
    ):
        self.scim_http_client = scim_http_client
        self.group_membership_resolver = group_membership_resolver
        self.settings = settings

    def write_udm_object(self, udm_object: object, topic: str) -> None:
        """
        Writes the record to the SCIM server.

        raises:
            ValueError: If no external_id is given.
        """
        scim_resource = self.prepare_data(udm_object, topic)
        if not scim_resource.external_id:
            raise ValueError("No external_id given!")
        try:
            existing = self.scim_http_client.get_resource(scim_resource.external_id, topic)
            scim_resource.id = existing["id"]
            scim_resource.meta = existing.get("meta")
        except ScimClientNoDataFoundException:
            self.scim_http_client.create_resource(scim_resource)
            return

        self.scim_http_client.update_resource(scim_resource)

    def delete(self, udm_object: object, topic: str) -> None:
        """
        Deletes the record in the SCIM server.

        raises:
            ValueError: If property defined in 'external_id_user_mapping' is not given.
        """

        if not hasattr(udm_object, "properties") or self.settings.external_id_user_mapping not in udm_object.properties:
            raise ValueError(f"No {self.settings.external_id_user_mapping} given!")

        try:
            existing = self.scim_http_client.get_resource(
                udm_object.properties[self.settings.external_id_user_mapping], topic
            )
        except ScimClientNoDataFoundException:
            return

        logger.info("Delete SCIM resource {} ({}).", existing["id"], existing["externalId"])

        self.scim_http_client.delete_resource(existing["id"], topic)

    def prepare_data(self, udm_object: object, topic: str) -> Resource:
        """
        Maps the data from UDM to SCIM

        raises:
            ValueError: If topic is not users/user or groups/group
        """
        user_model = self.scim_http_client.get_client().get_resource_model("User")
        user_extensions = user_model.get_extension_models()
        supported_extension_types = [
            extension for extension in _USER_EXTENSIONS if extension.to_schema().id in user_extensions
        ]
        user_type = (
            User[functools.reduce(operator.or_, supported_extension_types)] if supported_extension_types else User
        )

        mapper = UdmToScimMapper(
            cache=self.group_membership_resolver,
            user_type=user_type,
            group_type=Group,
            external_id_user_mapping=self.settings.external_id_user_mapping,
            external_id_group_mapping=self.settings.external_id_group_mapping,
            username_mapping=self.settings.username_mapping,
        )
        if topic == "users/user":
            scim_resource = mapper.map_user(udm_user=udm_object)
            scim_resource = user_type.model_validate(scim_resource.model_dump())
            _drop_unadvertised_attributes(scim_resource, user_type, user_model)
        elif topic == "groups/group":
            group_model = self.scim_http_client.get_client().get_resource_model("Group")
            scim_resource = mapper.map_group(udm_group=udm_object)
            scim_resource = Group.model_validate(scim_resource.model_dump())
            _drop_unadvertised_attributes(scim_resource, Group, group_model)
        else:
            raise ValueError(f"Unsupported message topic {topic}")

        logger.debug("Mapped resource:\n{}", cust_pformat(scim_resource))

        return scim_resource

    async def handle_udm_message(self, message: Message) -> None:
        """
        Handles provisioning messages for a SCIM client.
        """
        logger.debug("Message:\n{}", cust_pformat(message))

        if message.realm != "udm":
            raise ValueError(f"Unsupported message realm {message.realm}")

        if not message.body.new and not message.body.old:
            raise ValueError("Invalid message state.")

        if message.topic not in self.settings.modules:
            logger.debug("Skipping message for topic {}, not in allowed modules", message.topic)
            return

        if should_exist_in_scim(
            message, self.settings.scim_user_filter_attribute, self.settings.scim_group_filter_attribute
        ):
            udm_object = type("Obj", (object,), {k: v for k, v in message.body.new.items()})()
            self.write_udm_object(udm_object, message.topic)
        else:
            if message.body.old:
                udm_object = type("Obj", (object,), {k: v for k, v in message.body.old.items()})()
            else:
                # Happens when a create message with falsy user filter attribute is comming.
                # We check anyway if the record may exist in SCIM.
                udm_object = type("Obj", (object,), {k: v for k, v in message.body.new.items()})()

            self.delete(udm_object, message.topic)


def should_exist_in_scim(
    message: Message, user_filter_attribute: str | None, group_filter_attribute: str | None = None
) -> bool:
    """
    Returns the expected state in SCIM after processing the message.
    """
    if user_filter_attribute and message.topic == "users/user":
        result = bool(message.body.new["properties"].get(user_filter_attribute)) if message.body.new else False
        logger.debug("should_exist_in_scim: {} - By user filter attribute", result)
        return result

    if group_filter_attribute and message.topic == "groups/group":
        result = bool(message.body.new["properties"].get(group_filter_attribute)) if message.body.new else False
        logger.debug("should_exist_in_scim: {} - By group filter attribute", result)
        return result

    result = bool((not message.body.old) or message.body.new)
    logger.debug("should_exist_in_scim: {} - By message body", result)
    return result
