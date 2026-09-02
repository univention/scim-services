# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

from typing import cast

from loguru import logger
from scim2_models import Resource
from univention.provisioning.models import Message

from univention.scim.client.group_membership_resolver import GroupMembershipLdapResolver
from univention.scim.client.helper import cust_pformat
from univention.scim.client.scim_client_settings import ScimConsumerSettings
from univention.scim.client.scim_http_client import ScimClient, ScimClientNoDataFoundException
from univention.scim.transformation.udm2scim import UdmToScimMapper, supported_attribute_names


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

    def _external_id_mapping_for_topic(self, topic: str) -> str | None:
        if topic == "users/user":
            return cast(str | None, self.settings.external_id_user_mapping)
        if topic == "groups/group":
            return cast(str | None, self.settings.external_id_group_mapping)
        return None

    def _external_id_for(self, udm_object: object, topic: str) -> str | None:
        """Value of the UDM property that maps to SCIM externalId for `topic`."""
        mapping = self._external_id_mapping_for_topic(topic)
        if not mapping:
            return None
        return getattr(udm_object, "properties", {}).get(mapping)

    def write_udm_object(self, udm_object: object, topic: str) -> None:
        """
        Writes the record to the SCIM server.

        raises:
            ValueError: If no external_id is given.
        """
        resource_model = self.scim_http_client.get_resource_model_for_topic(topic)

        external_id = self._external_id_for(udm_object, topic)
        if not external_id:
            raise ValueError("No external_id given!")

        try:
            existing = self.scim_http_client.get_resource(external_id, resource_model)
            scim_resource = self.prepare_data(udm_object, topic, resource_model, exclude_immutable=True)
            scim_resource.id = existing["id"]
            scim_resource.meta = existing.get("meta")
            self.scim_http_client.update_resource(scim_resource)
        except ScimClientNoDataFoundException:
            scim_resource = self.prepare_data(udm_object, topic, resource_model, exclude_immutable=False)
            # id and meta are assigned by the service provider (RFC 7644 SS3.3) and must
            # not be sent on create.
            scim_resource.id = None
            scim_resource.meta = None
            self.scim_http_client.create_resource(scim_resource)

    def delete(self, udm_object: object, topic: str) -> None:
        """
        Deletes the record in the SCIM server.

        raises:
            ValueError: If the UDM property mapped to externalId for `topic` is not given.
        """
        external_id = self._external_id_for(udm_object, topic)
        if not external_id:
            raise ValueError(f"No {self._external_id_mapping_for_topic(topic)} given!")

        resource_model = self.scim_http_client.get_resource_model_for_topic(topic)

        try:
            existing = self.scim_http_client.get_resource(external_id, resource_model)
        except ScimClientNoDataFoundException:
            return

        logger.info("Delete SCIM resource {} ({}).", existing["id"], existing["externalId"])

        self.scim_http_client.delete_resource(existing["id"], resource_model)

    def prepare_data(
        self, udm_object: object, topic: str, resource_model: type[Resource], *, exclude_immutable: bool = False
    ) -> Resource:
        """
        Maps the data from UDM to SCIM

        `exclude_immutable`: pass `True` when the resource is being built for an update
        (PUT) rather than a create -- immutable attributes may only be set at creation
        (RFC 7643 SS7).

        raises:
            ValueError: If topic is not users/user or groups/group
        """
        mapper_kwargs = {
            "cache": self.group_membership_resolver,
            "external_id_user_mapping": self.settings.external_id_user_mapping,
            "external_id_group_mapping": self.settings.external_id_group_mapping,
            "username_mapping": self.settings.username_mapping,
        }

        supported_attributes = supported_attribute_names(resource_model, exclude_immutable=exclude_immutable)

        if topic == "users/user":
            mapper = UdmToScimMapper(
                user_type=resource_model, supported_attributes=supported_attributes, **mapper_kwargs
            )
            scim_resource = mapper.map_user(udm_user=udm_object)
            logger.debug("Mapped resource:\n{}", cust_pformat(scim_resource))
            return scim_resource

        if topic == "groups/group":
            mapper = UdmToScimMapper(
                group_type=resource_model, supported_attributes=supported_attributes, **mapper_kwargs
            )
            scim_resource = mapper.map_group(udm_group=udm_object)
            logger.debug("Mapped resource:\n{}", cust_pformat(scim_resource))
            return scim_resource

        raise ValueError(f"Unsupported message topic {topic}")

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
