#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

import asyncio

import httpx
from univention.provisioning.consumer.api import (
    MessageHandler,
    ProvisioningConsumerClient,
)

from univention.scim.consumer.authentication import Authenticator, AuthenticatorSettings
from univention.scim.consumer.group_membership_resolver import GroupMembershipLdapResolver, LdapSettings
from univention.scim.consumer.scim_client import ScimClient
from univention.scim.consumer.scim_consumer import ScimConsumer
from univention.scim.consumer.scim_consumer_settings import ScimConsumerSettings


async def main() -> None:
    settings = ScimConsumerSettings()
    auth = Authenticator(AuthenticatorSettings()) if settings.scim_oidc_authentication else httpx.Auth()
    scim_client = ScimClient(auth, settings)
    group_membership_resolver = GroupMembershipLdapResolver(scim_client, LdapSettings())
    scim_consumer = ScimConsumer(scim_client, group_membership_resolver, settings)

    async with ProvisioningConsumerClient() as client:
        await MessageHandler(client, [scim_consumer.handle_udm_message], pop_after_handling=True).run()


def run() -> None:
    asyncio.run(main())


if __name__ == "__main__":
    run()
