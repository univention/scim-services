# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH
from icecream import ic
from loguru import logger
from univention.provisioning.models.queue import ProvisioningMessage

from univention.scim.consumer.helper import vars_recursive
from univention.scim.consumer.scim_client import ScimClientWrapper
from univention.scim.transformation.udm2scim import UdmToScimMapper


async def handle_udm_message(message: ProvisioningMessage):
    logger.debug("ProvisioningMessage:\n{}", ic.format(vars_recursive(message)))

    if message.realm == "udm":
        todo = get_todo(message)
        #
        # Data preparation
        #
        if todo in ["create", "update"]:
            # Create object from message body new dict
            udm_resource = type("Obj", (object,), {k: v for k, v in message.body.new.items()})()

        elif todo == "delete":
            # Create object from message body old dict
            udm_resource = type("Obj", (object,), {k: v for k, v in message.body.old.items()})()

        else:
            logger.error("Unknown TODO {}", todo)

        if message.topic == "users/user":
            scim_resource = UdmToScimMapper().map_user(udm_user=udm_resource)

        elif message.topic == "groups/group":
            scim_resource = UdmToScimMapper().map_group(udm_group=udm_resource)

        logger.debug("Mapped resource:\n{}", ic.format(vars_recursive(scim_resource)))

        #
        # Message handling
        #
        if todo == "create":
            ScimClientWrapper().create_resource(scim_resource)

        elif todo == "update":
            ScimClientWrapper().update_resource(scim_resource)

        else:
            ScimClientWrapper().delete_resource(scim_resource)

    else:
        raise Exception("Na so nu nicht!")


def get_todo(message: ProvisioningMessage) -> str:
    if message.body.old and message.body.new:
        todo = "update"
    elif not message.body.old:
        todo = "create"
    elif not message.body.new:
        todo = "delete"

    return todo
