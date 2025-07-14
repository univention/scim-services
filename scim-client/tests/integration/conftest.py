# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

import multiprocessing
import os
import uuid
from collections.abc import Generator
from contextlib import suppress
from typing import Any

import httpx
import pytest
from loguru import logger
from univention.admin.rest.client import UDM, UnprocessableEntity

from univention.scim.client.group_membership_resolver import GroupMembershipLdapResolver, LdapSettings
from univention.scim.client.main import run as scim_client_run
from univention.scim.client.scim_client import ScimConsumer
from univention.scim.client.scim_client_settings import ScimConsumerSettings
from univention.scim.client.scim_http_client import ScimClient

from ..data.scim_helper import (
    create_provisioning_subscription,
    delete_provisioning_subscription,
    wait_for_resource_deleted,
)
from ..data.udm_helper import create_udm_group, delete_udm_group, delete_udm_user, generate_udm_users


@pytest.fixture(scope="session")
def downstream_udm_client() -> UDM:
    if "UNIVENTION_SCIM_SERVER" not in os.environ:
        return None

    logger.info("Create downstream udm_client.")
    udm = UDM.http(
        os.environ["DOWNSTREAM_UDM_BASE_URL"],
        os.environ["DOWNSTREAM_UDM_USERNAME"],
        os.environ["DOWNSTREAM_UDM_PASSWORD"],
    )

    return udm


@pytest.fixture(scope="session", autouse=True)
def downstream_maildomain(downstream_udm_client: ScimClient) -> Generator[str | None, None, None]:
    """
    Is only needed, when the tests are running against the
    Univention SCIM server. This uses UDM as backend and there
    we need the maildomain configuration too!
    """
    if "UNIVENTION_SCIM_SERVER" not in os.environ:
        yield None

    else:
        name = "scim-client.unittests"
        domains = downstream_udm_client.get("mail/domain")
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
def maildomain(udm_client: UDM) -> Generator[str, None, None]:
    name = "scim-client.unittests"
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
def group_data() -> dict[str, Any]:
    return {
        "name": "Test Group",
        "univentionObjectIdentifier": str(uuid.uuid4()),
        "users": [],
    }


@pytest.fixture(scope="function")
def user_data(maildomain: str) -> dict[str, Any]:
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
    # Univention extension
    user_data_with_extensions["PasswordRecoveryEmail"] = "recover@univention.test"
    # Customer1 extension
    user_data_with_extensions["primaryOrgUnit"] = "IT"
    user_data_with_extensions["secondaryOrgUnits"] = ["Support"]

    return user_data_with_extensions


@pytest.fixture(scope="session")
def udm_client() -> UDM:
    logger.info("Create udm_client.")
    udm = UDM.http(os.environ["UDM_BASE_URL"], os.environ["UDM_USERNAME"], os.environ["UDM_PASSWORD"])

    return udm


@pytest.fixture(scope="function")
def background_scim_client() -> Generator[bool, None, None]:
    logger.info("Fixture background_scim_client started.")

    create_provisioning_subscription()

    proc = multiprocessing.Process(target=scim_client_run)
    proc.start()

    yield True

    proc.terminate()

    delete_provisioning_subscription()

    logger.info("Fixture background_scim_client exited.")


@pytest.fixture(scope="function")
def background_scim_client_prefilled(
    udm_client: UDM, scim_http_client: ScimClient, group_data: dict[str, Any], maildomain: str
) -> Generator[Any, None, None]:
    logger.info("Fixture background_scim_client started.")

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
        wait_for_resource_deleted(scim_http_client, udm_user.properties.get("univentionObjectIdentifier"))
    delete_udm_group(udm_client=udm_client, group_data=group_data)
    wait_for_resource_deleted(
        scim_http_client=scim_http_client, univention_object_identifier=group_data["univentionObjectIdentifier"]
    )

    proc.terminate()

    delete_provisioning_subscription()

    logger.info("Fixture background_scim_client_prefilled exited.")


@pytest.fixture(scope="function")
def scim_client_settings() -> ScimConsumerSettings:
    """Settings are read from env to allow different configurations locally and in the testrunner container"""
    return ScimConsumerSettings()


@pytest.fixture(scope="function")
def scim_http_client(scim_client_settings: ScimConsumerSettings) -> Generator[ScimClient, None, None]:
    logger.info("Fixture scim_http_client start")
    scim_http_client = ScimClient(httpx.Auth(), scim_client_settings)

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
) -> ScimConsumer:
    scim_client = ScimConsumer(scim_http_client, group_membership_resolver, scim_client_settings)
    return scim_client


@pytest.fixture(scope="session", autouse=True)
def add_extended_attributes(udm_client: UDM) -> None:
    print("Adding extended attributes")
    module = udm_client.get("settings/extended_attribute")

    # Univention extended attribute PasswordRecoveryEmail
    udm_obj = module.new(position="cn=custom attributes,cn=univention,dc=univention-organization,dc=intranet")
    udm_obj.properties["name"] = "UniventionPasswordSelfServiceEmail"
    udm_obj.properties["CLIName"] = "PasswordRecoveryEmail"
    udm_obj.properties["module"] = ["users/user"]
    udm_obj.properties["default"] = ""
    udm_obj.properties["ldapMapping"] = "univentionPasswordSelfServiceEmail"
    udm_obj.properties["objectClass"] = "univentionPasswordSelfService"
    udm_obj.properties["shortDescription"] = "Password recovery e-mail address"
    udm_obj.properties["multivalue"] = False
    udm_obj.properties["valueRequired"] = False
    udm_obj.properties["mayChange"] = True
    udm_obj.properties["doNotSearch"] = False
    udm_obj.properties["deleteObjectClass"] = False
    udm_obj.properties["overwriteTab"] = False
    udm_obj.properties["fullWidth"] = True

    # ignore error 422, it is thrown if the attribute already exists
    with suppress(UnprocessableEntity):
        udm_obj.save()

    # Customer1 extended attribute primaryOrgUnit
    udm_obj = module.new(position="cn=custom attributes,cn=univention,dc=univention-organization,dc=intranet")
    udm_obj.properties["name"] = "Customer1PrimaryOrgUnit"
    udm_obj.properties["CLIName"] = "primaryOrgUnit"
    udm_obj.properties["module"] = ["users/user"]
    udm_obj.properties["default"] = ""
    udm_obj.properties["ldapMapping"] = "univentionFreeAttribute1"
    udm_obj.properties["objectClass"] = "univentionFreeAttributes"
    udm_obj.properties["shortDescription"] = "Customer1 primary org unit"
    udm_obj.properties["multivalue"] = False
    udm_obj.properties["valueRequired"] = False
    udm_obj.properties["mayChange"] = True
    udm_obj.properties["doNotSearch"] = False
    udm_obj.properties["deleteObjectClass"] = False
    udm_obj.properties["overwriteTab"] = False
    udm_obj.properties["fullWidth"] = True

    # ignore error 422, it is thrown if the attribute already exists
    with suppress(UnprocessableEntity):
        udm_obj.save()

    # Customer1 extended attribute secondaryOrgUnits
    udm_obj = module.new(position="cn=custom attributes,cn=univention,dc=univention-organization,dc=intranet")
    udm_obj.properties["name"] = "Customer1SecondaryOrgUnits"
    udm_obj.properties["CLIName"] = "secondaryOrgUnits"
    udm_obj.properties["module"] = ["users/user"]
    udm_obj.properties["default"] = ""
    udm_obj.properties["ldapMapping"] = "univentionFreeAttribute2"
    udm_obj.properties["objectClass"] = "univentionFreeAttributes"
    udm_obj.properties["shortDescription"] = "Customer1 primary secondary org units"
    udm_obj.properties["multivalue"] = True
    udm_obj.properties["valueRequired"] = False
    udm_obj.properties["mayChange"] = True
    udm_obj.properties["doNotSearch"] = False
    udm_obj.properties["deleteObjectClass"] = False
    udm_obj.properties["overwriteTab"] = False
    udm_obj.properties["fullWidth"] = True

    # ignore error 422, it is thrown if the attribute already exists
    with suppress(UnprocessableEntity):
        udm_obj.save()

    # Place to store user externalID extended attribute
    udm_obj = module.new(position="cn=custom attributes,cn=univention,dc=univention-organization,dc=intranet")
    udm_obj.properties["name"] = "TestUserExternalId"
    udm_obj.properties["CLIName"] = "testExternalId"
    udm_obj.properties["module"] = ["users/user"]
    udm_obj.properties["default"] = ""
    udm_obj.properties["ldapMapping"] = "univentionFreeAttribute3"
    udm_obj.properties["objectClass"] = "univentionFreeAttributes"
    udm_obj.properties["shortDescription"] = "Test external ID for users"
    udm_obj.properties["multivalue"] = False
    udm_obj.properties["valueRequired"] = False
    udm_obj.properties["mayChange"] = True
    udm_obj.properties["doNotSearch"] = False
    udm_obj.properties["deleteObjectClass"] = False
    udm_obj.properties["overwriteTab"] = False
    udm_obj.properties["fullWidth"] = True

    # ignore error 422, it is thrown if the attribute already exists
    with suppress(UnprocessableEntity):
        udm_obj.save()

    # Place to store group externalID extended attribute
    udm_obj = module.new(position="cn=custom attributes,cn=univention,dc=univention-organization,dc=intranet")
    udm_obj.properties["name"] = "TestGroupExternalId"
    udm_obj.properties["CLIName"] = "testExternalId"
    udm_obj.properties["module"] = ["groups/group"]
    udm_obj.properties["default"] = ""
    udm_obj.properties["ldapMapping"] = "univentionFreeAttribute4"
    udm_obj.properties["objectClass"] = "univentionFreeAttributes"
    udm_obj.properties["shortDescription"] = "Test external ID for groups"
    udm_obj.properties["multivalue"] = False
    udm_obj.properties["valueRequired"] = False
    udm_obj.properties["mayChange"] = True
    udm_obj.properties["doNotSearch"] = False
    udm_obj.properties["deleteObjectClass"] = False
    udm_obj.properties["overwriteTab"] = False
    udm_obj.properties["fullWidth"] = True

    # ignore error 422, it is thrown if the attribute already exists
    with suppress(UnprocessableEntity):
        udm_obj.save()
