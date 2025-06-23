# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

import multiprocessing
import os
import uuid

import httpx
import pytest
from loguru import logger
from univention.admin.rest.client import UDM

from univention.scim.consumer.group_membership_resolver import GroupMembershipLdapResolver, LdapSettings
from univention.scim.consumer.main import run as scim_client_run
from univention.scim.consumer.scim_client import ScimClient
from univention.scim.consumer.scim_consumer import ScimConsumer
from univention.scim.consumer.scim_consumer_settings import ScimConsumerSettings

from ..data.scim_helper import (
    create_provisioning_subscription,
    delete_provisioning_subscription,
    wait_for_resource_deleted,
)
from ..data.udm_helper import create_udm_group, delete_udm_group, delete_udm_user, generate_udm_users


@pytest.fixture(scope="session")
def scim_udm_client() -> UDM:
    if "UNIVENTION_SCIM_SERVER" not in os.environ:
        return None

    logger.info("Create SCIM udm_client.")
    udm = UDM.http(os.environ["SCIM_UDM_BASE_URL"], os.environ["SCIM_UDM_USERNAME"], os.environ["SCIM_UDM_PASSWORD"])

    return udm


@pytest.fixture(scope="session", autouse=True)
def scim_maildomain(scim_udm_client):
    """
    Is only needed, when the tests are running against the
    Univention SCIM server. This uses UDM as backend and there
    we need the maildomain configuration too!
    """
    if "UNIVENTION_SCIM_SERVER" not in os.environ:
        yield None

    else:
        name = "scim-consumer.unittests"
        domains = scim_udm_client.get("mail/domain")
        if maildomains := list(domains.search(f"name={name}")):
            maildomain = domains.get(maildomains[0].dn)
            logger.info(f"Using existing mail domain {maildomain!r} on UDM for SCIM.")
        else:
            maildomain = domains.new()
            maildomain.properties.update({"name": name})
            maildomain.save()
            logger.info(f"Created new mail domain {maildomain!r} on UDM for SCIM.")

        yield name

        maildomain.delete()
        logger.info(f"Deleted mail domain {maildomain!r} on UDM for SCIM.")


@pytest.fixture(scope="session")
def maildomain(udm_client):
    name = "scim-consumer.unittests"
    domains = udm_client.get("mail/domain")
    if maildomains := list(domains.search(f"name={name}")):
        maildomain = domains.get(maildomains[0].dn)
        logger.info(f"Using existing mail domain {maildomain!r}.")
    else:
        maildomain = domains.new()
        maildomain.properties.update({"name": name})
        maildomain.save()
        logger.info(f"Created new mail domain {maildomain!r}.")

    yield name

    maildomain.delete()
    logger.info(f"Deleted mail domain {maildomain!r}.")


@pytest.fixture(scope="function")
def group_data() -> dict:
    return {
        "name": "Test Group",
        "univentionObjectIdentifier": str(uuid.uuid4()),
        "users": [],
    }


@pytest.fixture(scope="function")
def user_data(maildomain) -> dict:
    return {
        "username": "testuser",
        "firstname": "Test",
        "lastname": "User",
        "univentionObjectIdentifier": str(uuid.uuid4()),
        "password": "univention",
        "displayName": "Test User",
        "mailPrimaryAddress": f"testuser@{maildomain}",
        "mailAlternativeAddress": [f"testuser.2@{maildomain}", f"testuser.3@{maildomain}"],
    }


@pytest.fixture
def user_data_updated(user_data: dict) -> dict:
    return {
        "username": user_data["username"],
        "firstname": user_data["firstname"],
        "lastname": user_data["lastname"],
        "univentionObjectIdentifier": user_data["univentionObjectIdentifier"],
        "password": "univention2",
        "displayName": "This is a testuser",
        "mailPrimaryAddress": user_data["mailPrimaryAddress"],
        "mailAlternativeAddress": user_data["mailAlternativeAddress"],
    }


@pytest.fixture(scope="session")
def udm_client() -> UDM:
    logger.info("Create udm_client.")
    udm = UDM.http(os.environ["UDM_BASE_URL"], os.environ["UDM_USERNAME"], os.environ["UDM_PASSWORD"])

    return udm


@pytest.fixture(scope="function")
def background_scim_consumer():
    logger.info("Fixture background_scim_consumer started.")

    create_provisioning_subscription()

    proc = multiprocessing.Process(target=scim_client_run)
    proc.start()

    yield True

    proc.terminate()

    delete_provisioning_subscription()

    logger.info("Fixture background_scim_consumer exited.")


@pytest.fixture(scope="function")
def background_scim_consumer_prefilled(udm_client, scim_client, group_data, maildomain):
    logger.info("Fixture background_scim_consumer started.")

    # Create UDM records
    udm_users = generate_udm_users(udm_client=udm_client, maildomain_name=maildomain, amount=10)
    for udm_user in udm_users:
        group_data["users"].append(udm_user.dn)
    udm_group = create_udm_group(udm_client=udm_client, group_data=group_data)

    create_provisioning_subscription()

    proc = multiprocessing.Process(target=scim_client_run)
    proc.start()

    yield udm_users, udm_group

    # Cleanup
    for udm_user in udm_users:
        delete_udm_user(
            udm_client=udm_client,
            user_data={"univentionObjectIdentifier": udm_user.properties.get("univentionObjectIdentifier")},
        )
    for udm_user in udm_users:
        wait_for_resource_deleted(scim_client, udm_user.properties.get("univentionObjectIdentifier"))
    delete_udm_group(udm_client=udm_client, group_data=group_data)
    wait_for_resource_deleted(
        scim_client=scim_client, univention_object_identifier=group_data["univentionObjectIdentifier"]
    )

    proc.terminate()

    delete_provisioning_subscription()

    logger.info("Fixture background_scim_consumer_prefilled exited.")


@pytest.fixture(scope="function")
def scim_consumer_settings():
    """Settings are read from env to allow different configurations locally and in the testrunner container"""
    return ScimConsumerSettings()


@pytest.fixture(scope="function")
def scim_client(scim_consumer_settings):
    logger.info("Fixture scim_client start")
    scim_client = ScimClient(httpx.Auth(), scim_consumer_settings)

    yield scim_client

    del scim_client
    logger.info("Fixture scim_client exit")


@pytest.fixture
def group_membership_resolver(scim_client):
    return GroupMembershipLdapResolver(scim_client, LdapSettings())


@pytest.fixture
def scim_consumer(scim_consumer_settings, scim_client, group_membership_resolver):
    scim_consumer = ScimConsumer(scim_client, group_membership_resolver, scim_consumer_settings)
    return scim_consumer
