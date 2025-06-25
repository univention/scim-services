# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH
import os
import random
import socket
import urllib.parse
from collections.abc import AsyncGenerator, Callable, Generator
from contextlib import _GeneratorContextManager, contextmanager, suppress
from typing import Any, TypeVar
from unittest.mock import MagicMock

import pytest
import requests
from _pytest.logging import LogCaptureFixture
from faker import Faker
from fastapi.testclient import TestClient
from loguru import logger
from scim2_models import Address, Email, Group, GroupMember, Name, Resource, User
from univention.admin.rest.client import UDM, UnprocessableEntity

from helpers.allow_all_authn import AllowAllAuthorization, AllowAllBearerAuthentication, OpenIDConnectConfigurationMock
from helpers.udm_client import MockUdm
from univention.scim.server.authn.authn import Authentication
from univention.scim.server.config import ApplicationSettings
from univention.scim.server.container import ApplicationContainer
from univention.scim.server.domain.group_service_impl import GroupServiceImpl
from univention.scim.server.domain.repo.crud_manager import CrudManager
from univention.scim.server.domain.repo.udm.crud_udm import CrudUdm
from univention.scim.server.domain.repo.udm.udm_id_cache import UdmIdCache
from univention.scim.server.domain.user_service_impl import UserServiceImpl
from univention.scim.server.main import make_app
from univention.scim.server.models.types import GroupWithExtensions, UserWithExtensions
from univention.scim.transformation import ScimToUdmMapper, UdmToScimMapper


T = TypeVar("T", bound=Resource)


# helper classes to simplify type hinting
class CreateUserFactory:
    def __init__(
        self,
        udm_client: UDM,
        scim2udm_mapper: ScimToUdmMapper,
        udm2scim_mapper: UdmToScimMapper,
        random_user_factory: Callable[[list[GroupMember]], UserWithExtensions],
    ) -> None:
        self.udm_client = udm_client
        self.scim2udm_mapper = scim2udm_mapper
        self.udm2scim_mapper = udm2scim_mapper
        self.random_user_factory = random_user_factory
        self.users: list[UserWithExtensions] = []

    async def __call__(self, groups: list[GroupMember] | None = None, /) -> UserWithExtensions:
        if groups is None:
            groups = []
        user = self.random_user_factory(groups)

        # First, make sure there's no existing user with the same username
        await ensure_user_deleted(self.udm_client, username=user.user_name)

        # Create new user
        module = self.udm_client.get("users/user")
        udm_obj = module.new()

        user_properties = self.scim2udm_mapper.map_user(user)
        for key, value in user_properties.items():
            udm_obj.properties[key] = value

        udm_obj.save()

        scim_user = self.udm2scim_mapper.map_user(udm_obj, base_url="http://testserver/scim/v2")
        self.users.append(scim_user)
        return scim_user

        return self.udm2scim_mapper.map_user(udm_obj, base_url="http://testserver/scim/v2")


class CreateGroupFactory:
    def __init__(
        self,
        udm_client: UDM,
        scim2udm_mapper: ScimToUdmMapper,
        udm2scim_mapper: UdmToScimMapper,
        random_group_factory: Callable[[list[GroupMember]], GroupWithExtensions],
    ) -> None:
        self.udm_client = udm_client
        self.scim2udm_mapper = scim2udm_mapper
        self.udm2scim_mapper = udm2scim_mapper
        self.random_group_factory = random_group_factory
        self.groups: list[GroupWithExtensions] = []

    async def __call__(self, members: list[GroupMember] | None = None, /) -> GroupWithExtensions:
        if members is None:
            members = []
        group = self.random_group_factory(members)

        # First, make sure there's no existing group with the same name
        await ensure_group_deleted(self.udm_client, group_name=group.display_name)

        # Create new group
        module = self.udm_client.get("groups/group")
        udm_obj = module.new()

        group_properties = self.scim2udm_mapper.map_group(group)
        for key, value in group_properties.items():
            udm_obj.properties[key] = value

        udm_obj.save()

        scim_group = self.udm2scim_mapper.map_group(udm_obj, base_url="http://testserver/scim/v2")
        self.groups.append(scim_group)
        return scim_group


@pytest.fixture
def application_settings(monkeypatch: pytest.MonkeyPatch) -> Generator[ApplicationSettings, None, None]:
    env = {
        "IDP_OPENID_CONFIGURATION_URL": os.environ.get("IDP_OPENID_CONFIGURATION_URL", "test"),
        "UDM_URL": os.environ.get("UDM_URL", "http://localhost:9979/univention/udm"),
        "UDM_USERNAME": os.environ.get("UDM_USERNAME", "admin"),
        "UDM_PASSWORD": os.environ.get("UDM_PASSWORD", "secret"),
        "HOST": os.environ.get("HOST", "https://scim.unit.test"),
        "EXTERNAL_ID_USER_MAPPING": os.environ.get("EXTERNAL_ID_USER_MAPPING", "testExternalId"),
        "EXTERNAL_ID_GROUP_MAPPING": os.environ.get("EXTERNAL_ID_GROUP_MAPPING", "testExternalId"),
    }
    for k, v in env.items():
        monkeypatch.setenv(k, v)
    # Don't use the application_settings function because we don't want caching for unit tests
    yield ApplicationSettings()


@pytest.fixture
def cache(udm_client: UDM | MockUdm) -> UdmIdCache:
    return UdmIdCache(udm_client, 120)


@pytest.fixture
def mappers(cache: UdmIdCache) -> tuple[ScimToUdmMapper, UdmToScimMapper]:
    scim2udm_mapper = ScimToUdmMapper(
        cache=cache,
        external_id_user_mapping="testExternalId",
        external_id_group_mapping="testExternalId",
        roles_user_mapping="scimRoles",
    )
    udm2scim_mapper = UdmToScimMapper[UserWithExtensions, GroupWithExtensions](
        cache=cache,
        user_type=UserWithExtensions,
        group_type=GroupWithExtensions,
        external_id_user_mapping="testExternalId",
        external_id_group_mapping="testExternalId",
        roles_user_mapping="scimRoles",
    )

    return scim2udm_mapper, udm2scim_mapper


@pytest.fixture
def mappers_no_cache() -> tuple[ScimToUdmMapper, UdmToScimMapper]:
    scim2udm_mapper = ScimToUdmMapper(
        external_id_user_mapping="testExternalId",
        external_id_group_mapping="testExternalId",
        roles_user_mapping="scimRoles",
    )
    udm2scim_mapper = UdmToScimMapper[UserWithExtensions, GroupWithExtensions](
        user_type=UserWithExtensions,
        group_type=GroupWithExtensions,
        external_id_user_mapping="testExternalId",
        external_id_group_mapping="testExternalId",
        roles_user_mapping="scimRoles",
    )

    return scim2udm_mapper, udm2scim_mapper


@contextmanager
def setup_mocks(
    application_settings: ApplicationSettings,
    udm_client: UDM | MockUdm,
    mappers: tuple[ScimToUdmMapper, UdmToScimMapper],
    host: str,
    api_prefix: str,
) -> Generator[None, None, None]:
    scim2udm_mapper, udm2scim_mapper = mappers

    user_repo = CrudUdm[UserWithExtensions](
        resource_type="User",
        scim2udm_mapper=scim2udm_mapper,
        udm2scim_mapper=udm2scim_mapper,
        resource_class=User,
        udm_client=udm_client,
        base_url=f"{host}{api_prefix}",
        external_id_mapping="testExternalId",
    )

    group_repo = CrudUdm[GroupWithExtensions](
        resource_type="Group",
        scim2udm_mapper=scim2udm_mapper,
        udm2scim_mapper=udm2scim_mapper,
        resource_class=Group,
        udm_client=udm_client,
        base_url=f"{host}{api_prefix}",
        external_id_mapping="testExternalId",
    )

    user_crud_manager = CrudManager[UserWithExtensions](user_repo, "User")
    group_crud_manager = CrudManager[GroupWithExtensions](group_repo, "Group")

    # Create service instances
    user_service = UserServiceImpl(user_crud_manager)
    group_service = GroupServiceImpl(group_crud_manager)

    # Make sure that for tests we allow all bearer
    with (
        ApplicationContainer.authenticator.override(AllowAllBearerAuthentication()),
        ApplicationContainer.authorization.override(AllowAllAuthorization()),
        ApplicationContainer.oidc_configuration.override(OpenIDConnectConfigurationMock()),
        ApplicationContainer.settings.override(application_settings),
        ApplicationContainer.user_repo.override(user_crud_manager),
        ApplicationContainer.group_repo.override(group_crud_manager),
        ApplicationContainer.user_service.override(user_service),
        ApplicationContainer.group_service.override(group_service),
    ):
        yield


# This fxture can be overwritten in a test to setup stuff after default mocks where setup
@pytest.fixture
def after_setup() -> Callable[[], _GeneratorContextManager[Any, None, None]]:
    @contextmanager
    def stub() -> Generator[None, None, None]:
        yield

    return stub


# This fxture can be overwritten in a test if it wants to force the use of the MockUDM
@pytest.fixture
def force_mock() -> bool:
    return False


@pytest.fixture
def client(
    application_settings: ApplicationSettings,
    udm_client: UDM | MockUdm,
    after_setup: Callable[[], _GeneratorContextManager[Any, None, None]],
    force_mock: bool,
    mappers: tuple[ScimToUdmMapper, UdmToScimMapper],
    host: str,
    api_prefix: str,
) -> Generator[TestClient, None, None]:
    if force_mock or skip_if_no_udm():
        with (
            setup_mocks(application_settings, udm_client, mappers, host, api_prefix),
            after_setup(),
            TestClient(make_app(application_settings), headers={"Authorization": "Bearer let-me-in"}) as client,
        ):
            yield client
    else:
        with (
            # Mock auth for now also when using real UDM
            ApplicationContainer.authenticator.override(AllowAllBearerAuthentication()),
            ApplicationContainer.oidc_configuration.override(OpenIDConnectConfigurationMock()),
            ApplicationContainer.authorization.override(AllowAllAuthorization()),
            # Use settings from unit tests
            ApplicationContainer.settings.override(application_settings),
            after_setup(),
            TestClient(make_app(application_settings), headers={"Authorization": "Bearer let-me-in"}) as client,
        ):
            yield client


@pytest.fixture
def caplog(caplog: LogCaptureFixture) -> Generator[LogCaptureFixture, None, None]:
    handler_id = logger.add(
        caplog.handler,
        format="{message}",
        level=0,
        filter=lambda record: record["level"].no >= caplog.handler.level,
        enqueue=False,  # Set to 'True' if your test is spawning child processes.
    )
    yield caplog
    logger.remove(handler_id)


@contextmanager
def maildomain(directory_importer_config: Any) -> Generator[str, None, None]:
    base_url = f"{directory_importer_config.udm.uri.rstrip('/')}/mail/domain/"
    auth = (directory_importer_config.udm.user, directory_importer_config.udm.password)
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json",
    }

    create_response = requests.post(
        base_url,
        auth=auth,
        headers=headers,
        json={
            "properties": {
                "name": "example.org",
                "objectFlag": [],
            },
            "position": "cn=domain,cn=mail,dc=univention-organization,dc=intranet",
        },
    )
    assert create_response.status_code == 201, (
        f"Failed to create domain: {create_response.status_code}, {create_response.text}"
    )

    yield create_response.json()

    delete_response = requests.delete(
        f"{base_url}cn=example.org,cn=domain,cn=mail,dc=univention-organization,dc=intranet",
        auth=auth,
        headers=headers,
    )
    assert delete_response.status_code == 204, (
        f"Failed to delete domain: {delete_response.status_code}, {delete_response.text}"
    )


def is_server_reachable(url: str, timeout: int = 2) -> bool:
    parsed_url = urllib.parse.urlparse(url)
    host = parsed_url.hostname
    port = parsed_url.port or (443 if parsed_url.scheme == "https" else 80)

    if not host:
        return False

    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except (TimeoutError, ConnectionRefusedError, OSError):
        return False


def skip_if_no_udm() -> bool:
    if os.environ.get("UNIT_TESTS_ONLY") == "1":
        return True

    udm_url = os.environ.get("UDM_URL", "http://localhost:9979/univention/udm")
    return not is_server_reachable(udm_url)


# auth


@pytest.fixture
def authenticator_mock() -> Authentication:
    mock = MagicMock(spec=Authentication)

    from univention.scim.server.container import ApplicationContainer

    with ApplicationContainer.authenticator.override(mock):
        yield mock


@pytest.fixture
def disable_auththentication(application_settings: ApplicationSettings) -> ApplicationSettings:
    application_settings.auth_enabled = False
    return application_settings


@pytest.fixture(scope="session", autouse=True)
def add_extended_attributes() -> None:
    if skip_if_no_udm():
        return

    udm_url = os.environ.get("UDM_URL", "http://localhost:9979/univention/udm")
    udm_username = os.environ.get("UDM_USERNAME", "admin")
    udm_password = os.environ.get("UDM_PASSWORD", "univention")

    print("Adding extended attributes")
    client = UDM.http(udm_url, udm_username, udm_password)
    module = client.get("settings/extended_attribute")

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

    # Univention extended attribute roles
    udm_obj = module.new(position="cn=custom attributes,cn=univention,dc=univention-organization,dc=intranet")
    udm_obj.properties["name"] = "UniventionScimRoles"
    udm_obj.properties["CLIName"] = "scimRoles"
    udm_obj.properties["module"] = ["users/user"]
    udm_obj.properties["default"] = ""
    udm_obj.properties["ldapMapping"] = "univentionFreeAttribute1"
    udm_obj.properties["objectClass"] = "univentionFreeAttributes"
    udm_obj.properties["shortDescription"] = "Roles mapped from scim"
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
    udm_obj.properties["ldapMapping"] = "univentionFreeAttribute2"
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
    udm_obj.properties["ldapMapping"] = "univentionFreeAttribute3"
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
    udm_obj.properties["ldapMapping"] = "univentionFreeAttribute4"
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
    udm_obj.properties["ldapMapping"] = "univentionFreeAttribute5"
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


@pytest.fixture
def udm_client(
    random_user_factory: Callable[[list[GroupMember]], UserWithExtensions],
    random_group_factory: Callable[[list[GroupMember]], GroupWithExtensions],
    force_mock: bool,
    mappers_no_cache: tuple[ScimToUdmMapper, UdmToScimMapper],
) -> Generator[UDM | MockUdm, None, None]:
    if force_mock or skip_if_no_udm():
        print("Using mocked UDM")
        scim2udm_mapper, _ = mappers_no_cache
        yield MockUdm(random_user_factory, random_group_factory, scim2udm_mapper)
    else:
        print("Using real UDM")
        udm_url = os.environ.get("UDM_URL", "http://localhost:9979/univention/udm")
        udm_username = os.environ.get("UDM_USERNAME", "admin")
        udm_password = os.environ.get("UDM_PASSWORD", "univention")

        class ConnectorConfig:
            class UdmConfig:
                def __init__(self) -> None:
                    self.uri = udm_url
                    self.user = udm_username
                    self.password = udm_password

            def __init__(self) -> None:
                self.udm = self.UdmConfig()

        with maildomain(ConnectorConfig()):
            client = UDM.http(udm_url, udm_username, udm_password)
            yield client

        # if using a real UDM make sure to delete all users and groups after a test
        try:
            module = client.get("users/user")
            results = list(module.search())
            if results:
                for result in results:
                    udm_obj = result.open()
                    print(f"Deleting existing user: {udm_obj.properties['username']}")
                    udm_obj.delete()

            module = client.get("groups/group")
            results = list(module.search())
            if results:
                for result in results:
                    udm_obj = result.open()
                    # Do not delete default groups
                    if udm_obj.properties["gidNumber"] <= 5007:
                        continue

                    print(f"Deleting existing group: {udm_obj.properties['name']}")
                    udm_obj.delete()
        except Exception as e:
            print(f"Error checking/deleting user: {e}")


fake = Faker()


def random_user_data() -> dict[str, str]:
    """Generate random user data to avoid conflicts with existing users"""
    username = f"test-{fake.user_name().replace('.', '-')}-{random.randint(1000, 9999)}"
    return {
        "username": username,
        "given_name": fake.first_name(),
        "family_name": fake.last_name(),
        "email": f"{username}@example.org",
        "personal_email": f"{username}.personal@example.org",
    }


def random_group_data() -> dict[str, str]:
    """Generate random group data to avoid conflicts with existing groups"""
    group_name = f"test-group-{fake.word()}-{random.randint(1000, 9999)}"
    return {"display_name": group_name}


async def ensure_user_deleted(udm_client: UDM, username: str | None = None, user_id: str | None = None) -> bool:
    """
    Ensure a user is deleted from the system.
    Search by username or user_id and delete if found.
    """
    try:
        module = udm_client.get("users/user")
        if username:
            filter_str = f"uid={username}"
        elif user_id:
            filter_str = f"univentionObjectIdentifier={user_id}"
        else:
            return False

        results = list(module.search(filter_str))
        if results:
            for result in results:
                udm_obj = result.open()
                print(f"Deleting existing user: {udm_obj.properties['username']}")
                udm_obj.delete()
            return True
        return False
    except Exception as e:
        print(f"Error checking/deleting user: {e}")
        return False


async def ensure_group_deleted(udm_client: UDM, group_name: str | None = None, group_id: str | None = None) -> bool:
    """
    Ensure a group is deleted from the system.
    Search by group_name or group_id and delete if found.
    """
    try:
        module = udm_client.get("groups/group")
        if group_name:
            filter_str = f"cn={group_name}"
        elif group_id:
            filter_str = f"univentionObjectIdentifier={group_id}"
        else:
            return False

        results = list(module.search(filter_str))
        if results:
            for result in results:
                udm_obj = result.open()
                print(f"Deleting existing group: {udm_obj.properties['name']}")
                udm_obj.delete()
            return True
        return False
    except Exception as e:
        print(f"Error checking/deleting group: {e}")
        return False


@pytest.fixture
def random_user_factory() -> Callable[[list[GroupMember]], UserWithExtensions]:
    """Create a factory function that returns a random user each time it's called"""

    def factory(groups: list[GroupMember] | None = None) -> UserWithExtensions:
        if groups is None:
            groups = []
        data = random_user_data()

        user = UserWithExtensions(
            id=fake.uuid4(),
            external_id=fake.uuid4(),
            user_name=data["username"],
            name=Name(
                given_name=data["given_name"],
                family_name=data["family_name"],
                formatted=f"{data['given_name']} {data['family_name']}",
            ).model_dump(),
            password="securepassword",
            display_name=f"{data['given_name']} {data['family_name']}",
            title="Senior Engineer",
            emails=[
                Email(value=data["email"], primary=True, type="work").model_dump(),
                Email(value=data["personal_email"], type="home").model_dump(),
            ],
            addresses=[
                Address(
                    formatted="123 Main St\nAnytown, CA 12345\nUSA",
                    street_address="123 Main St",
                    locality="Anytown",
                    region="CA",
                    postal_code="12345",
                    country="USA",
                    type="work",
                ).model_dump()
            ],
            active=True,
            preferred_language="en-US",
            user_type="employee",
            groups=groups,
            meta={},
        )

        return user

    return factory


@pytest.fixture
def random_user(random_user_factory: Callable[[list[GroupMember]], UserWithExtensions]) -> UserWithExtensions:
    """Create a single random user (for backwards compatibility)"""
    return random_user_factory([])


@pytest.fixture
async def create_random_user(
    random_user_factory: Callable[[list[GroupMember]], UserWithExtensions],
    udm_client: UDM,
    mappers: tuple[ScimToUdmMapper, UdmToScimMapper],
) -> AsyncGenerator[CreateUserFactory, None]:
    """Create a user factory fixture with proper cleanup"""
    scim2udm_mapper, udm2scim_mapper = mappers

    factory = CreateUserFactory(udm_client, scim2udm_mapper, udm2scim_mapper, random_user_factory)
    yield factory

    # Cleanup - delete the user
    for created_user in factory.users:
        try:
            await ensure_user_deleted(udm_client, user_id=created_user.id)
        except Exception as e:
            print(f"Error cleaning up test user: {e}")


@pytest.fixture
def random_group_factory() -> Callable[[list[GroupMember]], GroupWithExtensions]:
    """Create a factory function that returns a random group each time it's called"""

    def factory(members: list[GroupMember] | None = None) -> GroupWithExtensions:
        if members is None:
            members = []
        data = random_group_data()

        return GroupWithExtensions(
            id=fake.uuid4(),
            external_id=fake.uuid4(),
            display_name=data["display_name"],
            members=members,
            meta={},
        )

    return factory


@pytest.fixture
def random_group(random_group_factory: Callable[[list[GroupMember]], GroupWithExtensions]) -> GroupWithExtensions:
    """Create a single random group (for backwards compatibility)"""
    return random_group_factory([])


@pytest.fixture
async def create_random_group(
    random_group_factory: Callable[[list[GroupMember]], GroupWithExtensions],
    udm_client: UDM,
    mappers: tuple[ScimToUdmMapper, UdmToScimMapper],
) -> AsyncGenerator[CreateGroupFactory, None]:
    """Create a group factory fixture with proper cleanup"""
    scim2udm_mapper, udm2scim_mapper = mappers

    factory = CreateGroupFactory(udm_client, scim2udm_mapper, udm2scim_mapper, random_group_factory)
    yield factory

    # Cleanup - delete the group
    for created_group in factory.groups:
        try:
            await ensure_group_deleted(udm_client, group_id=created_group.id)
        except Exception as e:
            print(f"Error cleaning up test group: {e}")


@pytest.fixture
def api_prefix(application_settings: ApplicationSettings) -> str:
    """Get the API prefix for the SCIM server."""
    return str(application_settings.api_prefix)


@pytest.fixture
def host(application_settings: ApplicationSettings) -> str:
    """Get the API prefix for the SCIM server."""
    return str(application_settings.host).rstrip("/")


@pytest.fixture
def auth_headers() -> dict[str, str]:
    """Get authentication headers for API requests."""
    return {"Authorization": "Bearer test-token"}
