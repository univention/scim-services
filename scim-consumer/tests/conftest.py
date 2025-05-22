# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

import multiprocessing
import os
import random
import string
import uuid

import pytest
import pytest_asyncio
from aiohttp import ClientResponseError
from loguru import logger
from univention.admin.rest.client import UDM
from univention.provisioning.consumer.api import (
    ProvisioningConsumerClient,
    ProvisioningConsumerClientSettings,
    RealmTopic,
)

from univention.scim.consumer.helper import cust_pformat
from univention.scim.consumer.main import run as scim_client_run


@pytest_asyncio.fixture(scope="session")
async def provisioning_subscription():
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
            logger.info("Subscription {} created.", os.environ["PROVISIONING_API_USERNAME"])

        except ClientResponseError as e:
            logger.warning("{}, Create subscription error.", e)


@pytest.fixture(scope="session")
def udm_user():
    chars = string.ascii_letters
    size = 6
    random_string = "".join(random.choice(chars) for x in range(size))

    return {
        "username": f"testuser.{random_string}",
        "firstname": "testuser",
        "lastname": random_string,
        "univentionObjectIdentifier": str(uuid.uuid4()),
        "password": "univention",
    }


@pytest.fixture
def udm_user_updated(udm_user):
    udm_user["displayName"] = "This is a testuser"
    udm_user["password"] = "univention2"
    return udm_user


@pytest.fixture
def udm_client():
    logger.info("Fixture udm_client started.")
    udm = UDM.http(os.environ["UDM_BASE_URL"], os.environ["UDM_USERNAME"], os.environ["UDM_PASSWORD"])
    logger.info("Fixture udm_client stopped.")
    return udm


@pytest.fixture
def create_udm_user(udm_client, udm_user):
    logger.info("Fixture create_udm_user started.")
    logger.debug("udm_user:\n{}", cust_pformat(udm_user))

    module = udm_client.get("users/user")
    obj = module.new()
    for key, value in udm_user.items():
        obj.properties[key] = value
    obj.save()
    logger.info("Fixture create_udm_user stopped.")
    return True


@pytest.fixture
def update_udm_user(udm_client, udm_user_updated):
    logger.info("Fixture update_udm_user started.")
    logger.debug("udm_user_updated:\n{}", cust_pformat(udm_user_updated))

    module = udm_client.get("users/user")
    for result in module.search(f"univentionObjectIdentifier={udm_user_updated['univentionObjectIdentifier']}"):
        logger.info("Found user with uoi: {}", udm_user_updated["univentionObjectIdentifier"])
        obj = result.open()
        for key, value in udm_user_updated.items():
            obj.properties[key] = value

        obj.save()
        break
    logger.info("Fixture update_udm_user stopped.")
    return True


@pytest.fixture(scope="function")
def delete_udm_user(udm_client, udm_user):
    logger.info("Fixture delete_udm_user started.")
    logger.debug("udm_user:\n{}", cust_pformat(udm_user))

    module = udm_client.get("users/user")
    for result in module.search(f"univentionObjectIdentifier={udm_user['univentionObjectIdentifier']}"):
        logger.info("Found user with uoi: {}", udm_user["univentionObjectIdentifier"])
        obj = result.open()
        obj.delete()
        break
    logger.info("Fixture delete_udm_user stopped.")
    return True


@pytest.fixture
def scim_consumer(provisioning_subscription):
    logger.info("Fixture scim_consumer started.")

    proc = multiprocessing.Process(target=scim_client_run)
    proc.start()

    yield

    proc.terminate()

    logger.info("Fixture scim_consumer exited.")
