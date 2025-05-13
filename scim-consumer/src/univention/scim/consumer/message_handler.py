# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH
from icecream import ic
from loguru import logger
from univention.provisioning.models.queue import ProvisioningMessage

from univention.scim.consumer.scim_client import create_user, get_client, get_config as get_scim_config
from univention.scim.transformation.udm2scim import UdmToScimMapper


async def handle_udm_message(message: ProvisioningMessage):
    logger.debug("ProvisioningMessage:\n{}", ic.format(vars(message)))
    if message.realm == "udm":
        if message.topic == "users/user":
            handle_user(message)
        else:
            raise Exception(f"Topic {message.topic} not implemented yet!")

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


def handle_user(message: ProvisioningMessage):
    todo = get_todo(message)

    if todo == "create":
        udm_user = type("Obj", (object,), {k: v for k, v in message.body.new.items()})()

        scim_user = UdmToScimMapper().map_user(udm_user=udm_user)
        logger.debug("MappedUser:\n{}", ic.format(vars(scim_user)))

        client_config = get_scim_config()
        scim_client = get_client(client_config)
        create_user(scim_client, scim_user)

    else:
        raise Exception("Not implemented yet!")
