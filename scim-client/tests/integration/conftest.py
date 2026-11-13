# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2026 Univention GmbH

import os
import random
import uuid
from collections.abc import Callable, Generator
from typing import Any

import httpx2
import pytest
from faker import Faker
from loguru import logger
from univention.admin.rest.client import UDM, Object

from univention.provisioning.error_handling.db import DBSession
from univention.scim.client.group_membership_resolver import GroupMembershipLdapResolver, LdapSettings
from univention.scim.client.scim_client import ScimConsumer
from univention.scim.client.scim_client_settings import ScimConsumerSettings
from univention.scim.client.scim_http_client import ScimClient

from ..data.helper import BackgroundConsumer
from ..data.scim_helper import wait_for_resource_deleted
from ..data.udm_helper import UDMObjectJanitor, create_udm_group, delete_udm_group, delete_udm_user, generate_udm_users


@pytest.fixture(scope="session")
def fake(pytestconfig) -> Faker:
    """Initialize Faker with a reproducible seed."""
    seed = pytestconfig.getoption("--randomly-seed")
    if not seed:
        seed = random.randint(1000, 9999)
    seed = int(seed)
    Faker.seed(seed)
    logger.info(f"Faker seed: {seed} (use --randomly-seed={seed} to reproduce)")
    return Faker()


@pytest.fixture(scope="session")
def using_univention_scim_server() -> bool:
    """
    Whether we're testing against the univention SCIM server.

    We can run our integration tests against a reference server or against our
    own server implementation. The latter needs some extra setup in the
    downstream UDM (the separate UDM the server is connected to).
    """
    if "UNIVENTION_SCIM_SERVER" not in os.environ:
        return False
    try:
        assert os.environ["UNIVENTION_SCIM_SERVER"].lower() in ["true", "false"]
        assert "DOWNSTREAM_UDM_BASE_URL" in os.environ
        assert "DOWNSTREAM_UDM_USERNAME" in os.environ
        assert "DOWNSTREAM_UDM_PASSWORD" in os.environ
    except KeyError:
        return False
    except AssertionError as e:
        raise ValueError("invalid configuration of UNIVENTION_SCIM_SERVER") from e
    return os.environ["UNIVENTION_SCIM_SERVER"].lower() == "true"


@pytest.fixture(scope="session")
def udm_client() -> UDM:
    logger.info("Create udm_client.")
    udm = UDM.http(os.environ["UDM_BASE_URL"], os.environ["UDM_USERNAME"], os.environ["UDM_PASSWORD"])

    return udm


@pytest.fixture(scope="session")
def get_downstream_udm_client(using_univention_scim_server: bool) -> Callable[[], UDM]:
    udm_client = None

    def getter() -> UDM:
        if not using_univention_scim_server:
            raise ValueError(
                "attempt to get a downstream UDM client, but we're not configured to use the Univention SCIM server."
            )
        nonlocal udm_client
        if udm_client is None:
            logger.info("Create downstream udm_client.")
            udm_client = UDM.http(
                os.environ["DOWNSTREAM_UDM_BASE_URL"],
                os.environ["DOWNSTREAM_UDM_USERNAME"],
                os.environ["DOWNSTREAM_UDM_PASSWORD"],
            )
        return udm_client

    return getter


@pytest.fixture(scope="session")
def maildomain(
    udm_client: UDM, using_univention_scim_server: bool, get_downstream_udm_client: Callable[[], UDM]
) -> Generator[str]:
    """
    Get maildomain for testing.

    Creates the domain in UDM. If we're testing against a Univention SCIM
    server, also creates it in the downstream UDM.
    """

    def ensure_maildomain(udm_client: UDM, name: str) -> Object:
        domains = udm_client.get("mail/domain")
        assert domains is not None
        if maildomains := list(domains.search(f"name={name}")):
            assert maildomains[0].dn is not None
            maildomain = domains.get(maildomains[0].dn)
            logger.info(f"Using existing mail domain {maildomain!r} at {udm_client.uri}.")
        else:
            maildomain = domains.new()
            maildomain.properties.update({"name": name})
            maildomain.save()
            logger.info(f"Created new mail domain {maildomain!r} at {udm_client.uri}.")
        return maildomain

    udm_clients = [udm_client]
    if using_univention_scim_server:
        udm_clients.append(get_downstream_udm_client())
    name = "scim-client.tests"
    maildomains = [ensure_maildomain(udm_client, name) for udm_client in udm_clients]

    yield name

    for maildomain in maildomains:
        maildomain.delete()
        logger.info(f"Deleted mail domain {maildomain!r}.")


@pytest.fixture(scope="function")
def group_data(fake: Faker) -> dict[str, Any]:
    return {
        "name": f"Test Group {fake.unique.random_int()}",
        "univentionObjectIdentifier": str(uuid.uuid4()),
        "users": [],
    }


@pytest.fixture(scope="function")
def user_data(fake: Faker, maildomain: str) -> dict[str, Any]:
    username = fake.unique.user_name()
    return {
        "username": username,
        "firstname": "Test",
        "lastname": "User",
        "univentionObjectIdentifier": str(uuid.uuid4()),
        "password": "univention",
        "displayName": "Test User",
        "mailPrimaryAddress": f"{username}@{maildomain}",
        "mailAlternativeAddress": [f"{username}.2@{maildomain}", f"{username}.3@{maildomain}"],
    }


@pytest.fixture
def user_data_updated(user_data: dict[str, Any]) -> dict[str, Any]:
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


@pytest.fixture(scope="function")
def user_data_with_extensions(user_data: dict[str, Any]) -> dict[str, Any]:
    user_data_with_extensions = user_data.copy()
    # Enterprise extension
    user_data_with_extensions["employeeNumber"] = "4711"

    return user_data_with_extensions


@pytest.fixture
def udm_object_janitor(udm_client: UDM) -> UDMObjectJanitor:
    return UDMObjectJanitor(udm_client)


@pytest.fixture(scope="session")
def scim_server_base_url() -> str:
    return os.environ["SCIM_SERVER_BASE_URL"]


@pytest.fixture(scope="session")
def keycloak_base_url() -> str:
    return os.environ["KEYCLOAK_BASE_URL"]


@pytest.fixture(scope="session")
def background_consumer() -> Generator[None]:
    with BackgroundConsumer():
        yield


@pytest.fixture
def create_user_and_group(
    background_consumer: ScimConsumer,
    udm_client: UDM,
    scim_http_client: ScimClient,
    group_data: dict[str, Any],
    maildomain: str,
) -> Generator[Any, None, None]:
    # Create UDM records
    udm_users = generate_udm_users(udm_client=udm_client, maildomain_name=maildomain, amount=10)
    for udm_user in udm_users:
        group_data["users"].append(udm_user.dn)
    udm_group = create_udm_group(udm_client=udm_client, group_data=group_data)

    yield udm_users, udm_group

    # Cleanup
    for udm_user in udm_users:
        udm_user_del = delete_udm_user(
            udm_client=udm_client,
            user_data={"univentionObjectIdentifier": udm_user.properties.get("univentionObjectIdentifier")},
        )
        assert wait_for_resource_deleted(scim_http_client, udm_user_del)
    udm_group_del = delete_udm_group(udm_client=udm_client, group_data=group_data)
    assert wait_for_resource_deleted(scim_http_client, udm_group_del)


@pytest.fixture(scope="function")
def scim_client_settings() -> ScimConsumerSettings:
    """Settings are read from env to allow different configurations locally and in the testrunner container"""
    return ScimConsumerSettings()


@pytest.fixture(scope="function")
def scim_http_client(scim_client_settings: ScimConsumerSettings) -> Generator[ScimClient, None, None]:
    logger.info("Fixture scim_http_client start")
    scim_http_client = ScimClient(httpx2.Auth(), scim_client_settings)

    yield scim_http_client

    del scim_http_client
    logger.info("Fixture scim_http_client exit")


@pytest.fixture
def group_membership_resolver(scim_http_client: ScimClient) -> GroupMembershipLdapResolver:
    return GroupMembershipLdapResolver(scim_http_client, LdapSettings())


@pytest.fixture
def scim_client(
    scim_client_settings: ScimConsumerSettings,
    scim_http_client: ScimClient,
    group_membership_resolver: GroupMembershipLdapResolver,
    database: DBSession,
) -> ScimConsumer:
    scim_client = ScimConsumer(scim_http_client, group_membership_resolver, scim_client_settings, database)
    return scim_client
