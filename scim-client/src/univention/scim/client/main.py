#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

import asyncio

import httpx
from loguru import logger
from univention.provisioning.consumer.api import (
    MessageHandler,
    ProvisioningConsumerClient,
)

from univention.scim.client.authentication import Authenticator, AuthenticatorSettings
from univention.scim.client.group_membership_resolver import GroupMembershipLdapResolver, LdapSettings
from univention.scim.client.scim_client import ScimClient, ScimConsumer
from univention.scim.client.scim_client_settings import ScimConsumerSettings


async def main() -> None:
    settings = ScimConsumerSettings()
    auth = Authenticator(AuthenticatorSettings()) if settings.scim_oidc_authentication else httpx.Auth()
    scim_client = ScimClient(auth, settings)
    group_membership_resolver = GroupMembershipLdapResolver(scim_client, LdapSettings())
    scim_client = ScimConsumer(scim_client, group_membership_resolver, settings)

    async with ProvisioningConsumerClient() as client:
        logger.debug("Start listening for provisioning messages")
        await MessageHandler(client, [scim_client.handle_udm_message], pop_after_handling=True).run()


def run() -> None:
    asyncio.run(main())


if __name__ == "__main__":
    run()
