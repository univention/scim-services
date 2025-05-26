# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH
from loguru import logger
from scim2_models import Resource
from univention.provisioning.models.queue import ProvisioningMessage

from univention.scim.consumer.helper import cust_pformat
from univention.scim.consumer.scim_client import ScimClientWrapper
from univention.scim.transformation.udm2scim import UdmToScimMapper


async def handle_udm_message(message: ProvisioningMessage):
    """ """
    logger.debug("ProvisioningMessage:\n{}", cust_pformat(message))

    if message.realm != "udm":
        raise ValueError(f"Unsupported message realm {message.realm}")

    #
    scim_resource = prepare_data(message=message)

    # TODO What is the correct behavior?!
    if not scim_resource.external_id:
        logger.error("Resource has no externalId!\n{}", cust_pformat(scim_resource))
        return

    #
    # Message handling
    #
    scim_client = ScimClientWrapper()
    if not message.body.old and message.body.new:
        scim_client.create_resource(scim_resource)

    elif message.body.old and message.body.new:
        scim_client.update_resource(scim_resource)

    elif not message.body.new and message.body.old:
        scim_client.delete_resource(scim_resource)
    else:
        raise ValueError("Invalid message state.")


def prepare_data(message: ProvisioningMessage) -> Resource:
    """ """
    # Transform data from dict to obj, because the udm mapper needs an object!
    if (message.body.old and message.body.new) or (not message.body.old and message.body.new):
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
