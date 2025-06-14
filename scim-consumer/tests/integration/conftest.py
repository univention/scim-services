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

from univention.scim.consumer.main import run as scim_client_run
from univention.scim.consumer.scim_client import ScimClient


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
    return {
        "username": udm_user["username"],
        "firstname": udm_user["firstname"],
        "lastname": udm_user["lastname"],
        "univentionObjectIdentifier": udm_user["univentionObjectIdentifier"],
        "password": "univention2",
        "displayName": "This is a testuser",
    }


@pytest.fixture
def udm_client_fixture():
    logger.info("Create udm_client.")
    udm = UDM.http(os.environ["UDM_BASE_URL"], os.environ["UDM_USERNAME"], os.environ["UDM_PASSWORD"])

    return udm


@pytest.fixture(scope="function")
def scim_consumer(provisioning_subscription):
    logger.info("Fixture scim_consumer started.")

    proc = multiprocessing.Process(target=scim_client_run)
    proc.start()

    yield

    proc.terminate()

    logger.info("Fixture scim_consumer exited.")


@pytest.fixture(scope="function")
def scim_client():
    logger.info("Fixture scim_client start")
    scim_client = ScimClient()

    yield scim_client

    del scim_client
    logger.info("Fixture scim_client exit")
