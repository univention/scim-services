#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

import asyncio

from loguru import logger
from univention.provisioning.consumer.api import (
    MessageHandler,
    ProvisioningConsumerClient,
)

from univention.scim.client.group_membership_resolver import GroupMembershipLdapResolver, LdapSettings
from univention.scim.client.scim_client import ScimClient, ScimConsumer
from univention.scim.client.scim_client_settings import get_scim_consumer_settings


async def main() -> None:
    settings = get_scim_consumer_settings()
    scim_client = ScimClient(settings.auth, settings)
    group_membership_resolver = GroupMembershipLdapResolver(scim_client, LdapSettings())
    scim_client = ScimConsumer(scim_client, group_membership_resolver, settings)

    async with ProvisioningConsumerClient() as client:
        logger.debug("Start listening for provisioning messages")
        await MessageHandler(client, [scim_client.handle_udm_message], pop_after_handling=True).run()


def run() -> None:
    asyncio.run(main())


if __name__ == "__main__":
    run()
