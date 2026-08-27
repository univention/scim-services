#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

import asyncio

from loguru import logger
from univention.provisioning.consumer.api import (
    MessageHandler,
    ProvisioningConsumerClient,
)

from univention.provisioning.error_handling.db import DB_URL, DBSession, initialize_db
from univention.scim.client.group_membership_resolver import GroupMembershipLdapResolver, LdapSettings
from univention.scim.client.scim_client import ScimClient, ScimConsumer
from univention.scim.client.scim_client_settings import get_scim_consumer_settings


async def main() -> None:
    settings = get_scim_consumer_settings()

    # Initialize the SQL database
    logger.info("Initializing SQL database", url=DB_URL)
    try:
        initialize_db()
    except Exception:
        logger.error("Failed to initialize database. Shutting down.")
        raise

    scim_client = ScimClient(settings.auth, settings)
    scim_client.get_client()  # eager connect + capability verification

    group_membership_resolver = None
    if settings.group_sync_enabled:
        logger.warning("Group provisioning support is enabled. This feature is experimental.")
        group_membership_resolver = GroupMembershipLdapResolver(scim_client, LdapSettings())
    scim_consumer = ScimConsumer(scim_client, group_membership_resolver, settings)

    # Drain all pending tasks, e.g. from a previous run
    with DBSession() as db:
        scim_consumer._process_all_tasks_with_db(db)

    async with ProvisioningConsumerClient() as client:
        logger.debug("Start listening for provisioning messages")
        await MessageHandler(client, [scim_consumer.handle_udm_message], pop_after_handling=True).run()


def run() -> None:
    asyncio.run(main())


if __name__ == "__main__":
    run()
