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

    if message.realm == "udm":
        #
        todo = get_todo(message=message)
        #
        scim_resource = prepare_data(todo=todo, message=message)

        #
        # Message handling
        #
        scim_client = ScimClientWrapper()
        if todo == "create":
            scim_client.create_resource(scim_resource)

        elif todo == "update":
            scim_client.update_resource(scim_resource)

        else:
            scim_client.delete_resource(scim_resource)

    else:
        raise Exception(f"Unsupported message realm {message.realm}")


def get_todo(message: ProvisioningMessage) -> str:
    """ """
    if message.body.old and message.body.new:
        todo = "update"
    elif not message.body.old:
        todo = "create"
    elif not message.body.new:
        todo = "delete"

    return todo


def prepare_data(todo: str, message: ProvisioningMessage) -> Resource:
    """ """
    if todo in ["create", "update"]:
        # Create object from message body new dict
        udm_resource = type("Obj", (object,), {k: v for k, v in message.body.new.items()})()

    elif todo == "delete":
        # Create object from message body old dict
        udm_resource = type("Obj", (object,), {k: v for k, v in message.body.old.items()})()

    else:
        raise Exception(f"Unsupported todo {todo}")

    if message.topic == "users/user":
        scim_resource = UdmToScimMapper().map_user(udm_user=udm_resource)

    elif message.topic == "groups/group":
        scim_resource = UdmToScimMapper().map_group(udm_group=udm_resource)

    logger.debug("Mapped resource:\n{}", cust_pformat(scim_resource))

    return scim_resource
