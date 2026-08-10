# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

import asyncio
import os
import time
from typing import Any, Final

import httpx
from aiohttp import ClientResponseError
from loguru import logger
from univention.provisioning.consumer.api import (
    ProvisioningConsumerClient,
    ProvisioningConsumerClientSettings,
    RealmTopic,
)

from univention.scim.client.helper import cust_pformat
from univention.scim.client.scim_http_client import ScimClient, ScimClientNoDataFoundException


DEFAULT_MAX_ATTEMPTS: Final[int] = 48  # equals 6m every attempt sleeps for 5s


def _get_module_and_external_id(udm_object: object) -> str:
    if type(udm_object) is dict:
        return udm_object["objectType"], udm_object["properties"]["univentionObjectIdentifier"]
    else:
        return udm_object.object_type, udm_object.properties["univentionObjectIdentifier"]


def wait_for_resource_exists(
    scim_http_client: ScimClient,
    udm_object: object,
    max_attempts: int = DEFAULT_MAX_ATTEMPTS,
) -> dict | None:
    """ """
    udm_module, external_id = _get_module_and_external_id(udm_object)
    for i in range(1, max_attempts):
        try:
            logger.debug("Try to get resource with uoi: {}. Attemp {}", external_id, i)
            resource = scim_http_client.get_resource(external_id, udm_module)
        except Exception:
            time.sleep(5)
            continue
        else:
            logger.debug("Fetched resource data:\n{}", cust_pformat(resource))
            return resource

    return None


def wait_for_resource_updated(
    scim_http_client: ScimClient,
    udm_object: object,
    condition_attr: str,
    condition_val: Any,
    condition_func: Any = None,
    max_attempts: int = DEFAULT_MAX_ATTEMPTS,
) -> dict | None:
    """ """
    udm_module, external_id = _get_module_and_external_id(udm_object)
    for i in range(1, max_attempts):
        logger.debug("Try to get resource with uoi: {}. Attemp {}", external_id, i)
        resource = scim_http_client.get_resource(external_id, udm_module)
        if condition_val and resource.get(condition_attr) == condition_val:
            logger.debug("Fetched resource data:\n{}", cust_pformat(resource))
            return resource
        if condition_func and condition_func(resource):
            return resource

        time.sleep(5)

    return None


def wait_for_resource_deleted(
    scim_http_client: ScimClient,
    udm_object: object,
    max_attempts: int = DEFAULT_MAX_ATTEMPTS,
) -> bool:
    """ """
    udm_module, external_id = _get_module_and_external_id(udm_object)
    try:
        for i in range(1, max_attempts):
            logger.info("Try to get user with uoi: {}. Attemp {}", external_id, i)
            scim_http_client.get_resource(external_id, udm_module)
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
                    # do not request prefill to speed up tests, in the tests we are only interested
                    # in the new users/groups created within the test not all the default users/groups
                    request_prefill=False,
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


def capture_authorization_header(scim_server_base_url: str, auth: httpx.Auth | None) -> str | None:
    captured: dict[str, str | None] = {}

    def capture(request: httpx.Request) -> None:
        captured["authorization"] = request.headers.get("Authorization")

    with httpx.Client(base_url=scim_server_base_url, auth=auth, event_hooks={"request": [capture]}) as client:
        response = client.get("/ServiceProviderConfig")

    assert response.status_code == 200
    return captured.get("authorization")
