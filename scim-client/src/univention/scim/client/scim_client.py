# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

from loguru import logger
from scim2_models import EnterpriseUser, Group, Resource
from univention.provisioning.models import Message

from univention.scim.client.group_membership_resolver import GroupMembershipLdapResolver
from univention.scim.client.helper import cust_pformat
from univention.scim.client.scim_client_settings import ScimConsumerSettings
from univention.scim.client.scim_http_client import ScimClient, ScimClientNoDataFoundException

# FIXME: Use the models from the server for now because the original models are to strict
#        For example with the email type.
#        In the future the mapper should not operate on pydantic models but just dictionaries
from univention.scim.server.models.user import User
from univention.scim.transformation.udm2scim import UdmToScimMapper


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
            existing_scim_resource = self.scim_http_client.get_resource_by_external_id(scim_resource.external_id)
        except ScimClientNoDataFoundException:
            self.scim_http_client.create_resource(scim_resource)
            return
        scim_resource.id = existing_scim_resource.id
        scim_resource.meta = existing_scim_resource.meta

        self.scim_http_client.update_resource(scim_resource)

    def delete(self, udm_object: object, topic: str) -> None:
        """
        Deletes the record in the SCIM server.

        raises:
            ValueError: If no external_id is given.
        """
        scim_resource = self.prepare_data(udm_object, topic)
        if not scim_resource.external_id:
            raise ValueError("No external_id given!")

        try:
            existing_scim_resource = self.scim_http_client.get_resource_by_external_id(scim_resource.external_id)
        except ScimClientNoDataFoundException:
            return
        self.scim_http_client.delete_resource(existing_scim_resource)

    def prepare_data(self, udm_object: object, topic: str) -> Resource:
        """
        Maps the data from UDM to SCIM

        raises:
            ValueError: If topic is not users/user or groups/group
        """
        mapper = UdmToScimMapper(
            cache=self.group_membership_resolver,
            # FIXME: We can`t use the discovered types here because the dynamically crated pydantic model has
            #        some limitations.
            #        Should be fixed if the mapper does not use pydantic types.anymore.
            # user_type=self.scim_http_client.get_client().get_resource_model("User"),
            # group_type=self.scim_http_client.get_client().get_resource_model("Group"),
            user_type=User[EnterpriseUser],
            group_type=Group,
            external_id_user_mapping=self.settings.external_id_user_mapping,
            external_id_group_mapping=self.settings.external_id_group_mapping,
        )
        if topic == "users/user":
            scim_resource = mapper.map_user(udm_user=udm_object)
            # FIXME: The scim client validates the response of a message with the pydantic model given in the request.
            #        Make sure to use the correct pydantic model required by the server
            scim_resource = (
                self.scim_http_client.get_client().get_resource_model("User").model_validate(scim_resource.model_dump())
            )
        elif topic == "groups/group":
            scim_resource = mapper.map_group(udm_group=udm_object)
            # FIXME: The scim client validates the response of a message with the pydantic model given in the request.
            #        Make sure to use the correct pydantic model required by the server
            scim_resource = (
                self.scim_http_client.get_client()
                .get_resource_model("Group")
                .model_validate(scim_resource.model_dump())
            )
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

        if should_exist_in_scim(message, self.settings.scim_user_filter_attribute):
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


def should_exist_in_scim(message: Message, user_filter_attribute: str | None) -> bool:
    """
    Returns the expected state in SCIM after processing the message.
    """
    should_exist_in_scim = bool((not message.body.old) or message.body.new)
    logger.debug("should_exist_in_scim: {} - By message body", should_exist_in_scim)

    if user_filter_attribute and message.topic == "users/user":
        should_exist_in_scim = (
            bool(message.body.new["properties"].get(user_filter_attribute)) if message.body.new else False
        )
        logger.debug("should_exist_in_scim: {} - By user filter attribute", should_exist_in_scim)

    return should_exist_in_scim
