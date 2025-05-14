#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

import asyncio

from loguru import logger
from univention.provisioning.consumer.api import (
    MessageHandler,
    ProvisioningConsumerClient,
)

from univention.scim.consumer.message_handler import handle_udm_message


async def main() -> None:
    logger.info("Listening for messages")
    async with ProvisioningConsumerClient() as client:
        await MessageHandler(client, [handle_udm_message], pop_after_handling=True).run()


def run():
    asyncio.run(main())


if __name__ == "__main__":
    run()
