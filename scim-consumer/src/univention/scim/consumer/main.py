#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

import asyncio
from typing import NamedTuple

from loguru import logger
from univention.provisioning.consumer.api import (
    MessageHandler,
    MessageHandlerSettings,
    ProvisioningConsumerClient,
    ProvisioningConsumerClientSettings,
)

from univention.scim.consumer.message_handler import handle_udm_message


class Config(NamedTuple):
    base_url: str
    admin_username: str
    admin_password: str
    realm: str
    topic: str
    log_level: str
    max_acknowledgement_retries: int


def get_config() -> Config:
    provisioning_api_base_url = "http://localhost:7777/"
    provisioning_api_username = "scim-consumer"
    provisioning_api_password = "univention"
    realm = "udm"
    topic = "users/user"
    log_level = "INFO"
    max_acknowledgement_retries = 10

    return Config(
        base_url=provisioning_api_base_url,
        admin_username=provisioning_api_username,
        admin_password=provisioning_api_password,
        realm=realm,
        topic=topic,
        log_level=log_level,
        max_acknowledgement_retries=max_acknowledgement_retries,
    )


async def main(config: Config) -> None:
    pcc_settings = ProvisioningConsumerClientSettings(
        provisioning_api_base_url=config.base_url,
        provisioning_api_username=config.admin_username,
        provisioning_api_password=config.admin_password,
        log_level=config.log_level,
    )
    mh_settings = MessageHandlerSettings(max_acknowledgement_retries=config.max_acknowledgement_retries)

    logger.info("Listening for messages")
    async with ProvisioningConsumerClient(pcc_settings) as client:
        await MessageHandler(client, [handle_udm_message], mh_settings).run()


def run():
    config = get_config()
    asyncio.run(main(config))

if __name__ == "__main__":
    run()
