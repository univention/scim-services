# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

from loguru import logger
from univention.provisioning.models.queue import ProvisioningMessage

from univention.scim.consumer.helper import cust_pformat
from univention.scim.consumer.scim_consumer import ScimConsumer
from univention.scim.consumer.scim_consumer_settings import ScimConsumerSettings


async def handle_udm_message(message: ProvisioningMessage):
    """
    Handles provisioning messages for a SCIM consumer.

    """
    logger.debug("ProvisioningMessage:\n{}", cust_pformat(message))

    if message.realm != "udm":
        raise ValueError(f"Unsupported message realm {message.realm}")

    if not message.body.new and not message.body.old:
        raise ValueError("Invalid message state.")

    user_filter_attribute = ScimConsumerSettings().scim_user_filter_attribute

    should_exist_in_scim = get_should_exist_in_scim(message=message, user_filter_attribute=user_filter_attribute)

    scim_consumer = ScimConsumer()
    if should_exist_in_scim:
        udm_object = type("Obj", (object,), {k: v for k, v in message.body.new.items()})()
        scim_consumer.write_udm_object(udm_object, message.topic)
    else:
        if message.body.old:
            udm_object = type("Obj", (object,), {k: v for k, v in message.body.old.items()})()
        else:
            # Happens when a create message with falsy user filter attribute is comming.
            # We check anyway if the record may exist in SCIM.
            udm_object = type("Obj", (object,), {k: v for k, v in message.body.new.items()})()

        scim_consumer.delete_udm_object(udm_object, message.topic)


def get_should_exist_in_scim(message: ProvisioningMessage, user_filter_attribute: str) -> bool:
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
