# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

# from functools import lru_cache

from loguru import logger
from pydantic_settings import BaseSettings
from scim2_models import Resource
from univention.provisioning.models.queue import ProvisioningMessage

from univention.scim.consumer.helper import cust_pformat
from univention.scim.consumer.scim_client import ScimClientNoDataFoundException, ScimClientWrapper
from univention.scim.transformation.udm2scim import UdmToScimMapper


class MessageHandlerSettings(BaseSettings):
    # Attribute in the UDM user object that controls SCIM processing.
    # If it is truthy , the object will be transfered to SCIM.
    scim_user_filter_attribute: str | None = None

    def __new__(cls, *args, **kwargs):
        """
        Singleton pattern
        """
        if not hasattr(cls, "instance"):
            cls.instance = super().__new__(cls)
        return cls.instance


async def handle_udm_message(message: ProvisioningMessage):
    """
    Handles provisioning messages for a SCIM consumer.

    """
    logger.debug("ProvisioningMessage:\n{}", cust_pformat(message))

    if message.realm != "udm":
        raise ValueError(f"Unsupported message realm {message.realm}")

    scim_resource = prepare_data(message=message)

    # TODO What is the correct behavior?!
    if not scim_resource.external_id:
        logger.error("Resource has no externalId!\n{}", cust_pformat(scim_resource))
        return

    scim_client = ScimClientWrapper()
    settings = MessageHandlerSettings()

    transaction_type = get_required_action(
        message=message,
        scim_client=scim_client,
        scim_external_id=scim_resource.external_id,
        scim_user_filter_attribute=settings.scim_user_filter_attribute,
    )

    #
    # Message handling
    #
    if transaction_type == "CREATE":
        scim_client.create_resource(scim_resource)

    elif transaction_type == "UPDATE":
        scim_client.update_resource(scim_resource)

    elif transaction_type == "DELETE":
        scim_client.delete_resource(scim_resource)
    else:
        logger.debug("Nothing to do. Message skipped.")


def get_required_action(
    message: ProvisioningMessage,
    scim_client: ScimClientWrapper,
    scim_external_id: str,
    scim_user_filter_attribute: str,
):
    """
    Returns the action for the transaction.

    Checks the message body and an optional filter.
    When the filter is set, the state of the resource in the SCIM server
    will be checked too.
    """
    required_action = None

    # Check if the resource exists in SCIM
    try:
        scim_client.get_resource_by_external_id(scim_external_id)
    except ScimClientNoDataFoundException:
        resource_exists_in_scim = False
    else:
        resource_exists_in_scim = True

    logger.debug("resource_exists_in_scim[{}]: {}", scim_external_id, resource_exists_in_scim)
    logger.debug("message.body.old[{}]: {}", scim_external_id, bool(message.body.old))
    logger.debug("message.body.new[{}]: {}", scim_external_id, bool(message.body.new))

    # Get transaction type by message body state
    if message.body.new and not resource_exists_in_scim:
        required_action = "CREATE"

    elif message.body.new and resource_exists_in_scim:
        required_action = "UPDATE"

    elif not message.body.new and message.body.old and resource_exists_in_scim:
        required_action = "DELETE"

    else:
        return None

    logger.debug("Transaction type by message body state {}", required_action)

    # Get transaction type by filter attribute.
    # Only for users!
    user_filter_old = False
    user_filter_new = False
    if message.topic == "users/user" and scim_user_filter_attribute:
        # Get filter state from message body
        if message.body.new:
            user_filter_new = bool(message.body.new["properties"].get(scim_user_filter_attribute))
        if message.body.old:
            user_filter_old = bool(message.body.old["properties"].get(scim_user_filter_attribute))

        logger.debug("user_filter_old: {}", user_filter_old)
        logger.debug("user_filter_new: {}", user_filter_new)

        # Calculate transaction type.
        if user_filter_new and resource_exists_in_scim:
            required_action = "UPDATE"
        elif user_filter_new and not resource_exists_in_scim:
            required_action = "CREATE"
        elif user_filter_old and not user_filter_new and resource_exists_in_scim:
            required_action = "DELETE"
        else:
            required_action = None

        logger.debug("Transaction type by user filter attribute {}", required_action)

    return required_action


def prepare_data(message: ProvisioningMessage) -> Resource:
    """
    Maps the data from UDM to SCIM

    """
    # Transform data from dict to obj, because the udm mapper needs an object!
    if message.body.new:
        # Create object from message body new dict
        udm_resource = type("Obj", (object,), {k: v for k, v in message.body.new.items()})()

    elif not message.body.new and message.body.old:
        # Create object from message body old dict
        udm_resource = type("Obj", (object,), {k: v for k, v in message.body.old.items()})()

    else:
        raise ValueError("Invalid message state.")

    mapper = UdmToScimMapper()
    if message.topic == "users/user":
        scim_resource = mapper.map_user(udm_user=udm_resource)

    elif message.topic == "groups/group":
        scim_resource = mapper.map_group(udm_group=udm_resource)

    else:
        raise ValueError(f"Unsupported message topic {message.topic}")

    logger.debug("Mapped resource:\n{}", cust_pformat(scim_resource))

    return scim_resource
