# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

import asyncio
import os
import time
from typing import Any

from aiohttp import ClientResponseError
from loguru import logger
from scim2_models import Resource
from univention.provisioning.consumer.api import (
    ProvisioningConsumerClient,
    ProvisioningConsumerClientSettings,
    RealmTopic,
)

from univention.scim.client.helper import cust_pformat
from univention.scim.client.scim_http_client import ScimClient, ScimClientNoDataFoundException


def wait_for_resource_exists(
    scim_http_client: ScimClient, univention_object_identifier: str, max_attemps: int = 100
) -> Resource | None:
    """ """
    for i in range(1, max_attemps or 100):
        try:
            logger.debug("Try to get resource with uoi: {}. Attemp {}", univention_object_identifier, i)
            resource = scim_http_client.get_resource_by_external_id(univention_object_identifier)
        except Exception:
            time.sleep(5)
            continue
        else:
            logger.debug("Fetched resource data:\n{}", cust_pformat(resource))
            return resource

    return None


def wait_for_resource_updated(
    scim_http_client: ScimClient,
    univention_object_identifier: str,
    condition_attr: str,
    condition_val: Any,
    max_attemps: int = 100,
) -> Resource | None:
    """ """
    for i in range(1, max_attemps or 100):
        logger.debug("Try to get resource with uoi: {}. Attemp {}", univention_object_identifier, i)
        resource = scim_http_client.get_resource_by_external_id(univention_object_identifier)
        if getattr(resource, condition_attr) == condition_val:
            logger.debug("Fetched resource data:\n{}", cust_pformat(resource))
            return resource
        else:
            time.sleep(5)

    return None


def wait_for_resource_deleted(
    scim_http_client: ScimClient, univention_object_identifier: str, max_attemps: int = 100
) -> bool:
    """ """
    try:
        for i in range(1, max_attemps or 100):
            logger.info("Try to get user with uoi: {}. Attemp {}", univention_object_identifier, i)
            scim_http_client.get_resource_by_external_id(univention_object_identifier)
            time.sleep(5)
        return False

    except ScimClientNoDataFoundException:
        return True


def create_provisioning_subscription() -> None:
    """ """

    async def create_provisioning_subscription_async() -> None:
        admin_settings = ProvisioningConsumerClientSettings(
            provisioning_api_base_url=os.environ["PROVISIONING_API_BASE_URL"],
            provisioning_api_username=os.environ["PROVISIONING_API_ADMIN_USERNAME"],
            provisioning_api_password=os.environ["PROVISIONING_API_ADMIN_PASSWORD"],
            log_level="DEBUG",
        )
        async with ProvisioningConsumerClient(admin_settings) as admin_client:
            try:
                await admin_client.create_subscription(
                    name=os.environ["PROVISIONING_API_USERNAME"],
                    password=os.environ["PROVISIONING_API_PASSWORD"],
                    realms_topics=[
                        RealmTopic(realm="udm", topic="users/user"),
                        RealmTopic(realm="udm", topic="groups/group"),
                    ],
                    request_prefill=True,
                )
            except ClientResponseError as e:
                logger.warning("%s, Client already exists", e)
            else:
                logger.info("Subscription {} created.", os.environ["PROVISIONING_API_USERNAME"])

    asyncio.run(create_provisioning_subscription_async())


def delete_provisioning_subscription() -> None:
    """ """

    async def delete_provisioning_subscription_async() -> None:
        admin_settings = ProvisioningConsumerClientSettings(
            provisioning_api_base_url=os.environ["PROVISIONING_API_BASE_URL"],
            provisioning_api_username=os.environ["PROVISIONING_API_ADMIN_USERNAME"],
            provisioning_api_password=os.environ["PROVISIONING_API_ADMIN_PASSWORD"],
            log_level="DEBUG",
        )
        async with ProvisioningConsumerClient(admin_settings) as admin_client:
            await admin_client.cancel_subscription(name=os.environ["PROVISIONING_API_USERNAME"])
            logger.info("Subscription {} deleted.", os.environ["PROVISIONING_API_USERNAME"])

    asyncio.run(delete_provisioning_subscription_async())
