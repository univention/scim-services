# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH
import os
import random
import socket
import urllib.parse
from collections.abc import AsyncGenerator, Generator
from typing import Any, TypeVar
from unittest.mock import MagicMock

import pytest
import requests
from _pytest.logging import LogCaptureFixture
from faker import Faker
from fastapi.testclient import TestClient
from loguru import logger
from scim2_models import Address, Email, Group, Name, Resource, User
from univention.admin.rest.client import UDM

from helpers.allow_all_authn import AllowAllBearerAuthentication, OpenIDConnectConfigurationMock
from helpers.mock_udm import MockCrudUdm
from univention.scim.server.authn.authn import Authentication
from univention.scim.server.config import ApplicationSettings
from univention.scim.server.container import ApplicationContainer
from univention.scim.server.domain.group_service_impl import GroupServiceImpl
from univention.scim.server.domain.repo.crud_manager import CrudManager
from univention.scim.server.domain.repo.udm.crud_udm import CrudUdm
from univention.scim.server.domain.user_service_impl import UserServiceImpl
from univention.scim.server.main import app
from univention.scim.server.model_service.scim2udm import ScimToUdmMapper
from univention.scim.server.model_service.udm2scim import UdmToScimMapper


T = TypeVar("T", bound=Resource)


@pytest.fixture(autouse=True)
def application_settings(monkeypatch: pytest.MonkeyPatch) -> Generator[ApplicationSettings, None, None]:
    env = {
        "IDP_OPENID_CONFIGURATION_URL": os.environ.get("IDP_OPENID_CONFIGURATION_URL", "test"),
        "UDM_URL": os.environ.get("UDM_URL", "http://localhost:9979/univention/udm"),
        "UDM_USERNAME": os.environ.get("UDM_USERNAME", "admin"),
        "UDM_PASSWORD": os.environ.get("UDM_PASSWORD", "secret"),
    }
    for k, v in env.items():
        monkeypatch.setenv(k, v)
    # Don't use the application_settings function because we don't want caching for unit tests
    yield ApplicationSettings()


@pytest.fixture
def setup_mocks(application_settings: ApplicationSettings) -> Generator[None, None, None]:
    # Create test UDM repositories
    ScimToUdmMapper()
    UdmToScimMapper()

    user_repo = MockCrudUdm[User](
        resource_type="User",
        udm_url="http://test.local",
    )

    group_repo = MockCrudUdm[Group](
        resource_type="Group",
    )

    user_crud_manager = CrudManager[User](user_repo, "User")
    group_crud_manager = CrudManager[Group](group_repo, "Group")

    # Create service instances
    user_service = UserServiceImpl(user_crud_manager)
    group_service = GroupServiceImpl(group_crud_manager)

    # Make sure that for tests we allow all bearer
    with (
        ApplicationContainer.authenticator.override(AllowAllBearerAuthentication()),
        ApplicationContainer.oidc_configuration.override(OpenIDConnectConfigurationMock()),
        ApplicationContainer.settings.override(application_settings),
        ApplicationContainer.user_repo.override(user_crud_manager),
        ApplicationContainer.group_repo.override(group_crud_manager),
        ApplicationContainer.user_service.override(user_service),
        ApplicationContainer.group_service.override(group_service),
    ):
        yield


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    with TestClient(app, headers={"Authorization": "Bearer let-me-in"}) as client:
        yield client

    # remove routes to make sure they are re-added when reusing
    # global app object with updated parameters like disabled authentication
    app.router.routes = []

    # setup OpenAPI routes again
    app.setup()


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


def create_crud_manager(
    resource_type: str, resource_class: type[User | Group], udm_url: str, udm_username: str, udm_password: str
) -> CrudManager:
    scim2udm_mapper = ScimToUdmMapper()
    udm2scim_mapper = UdmToScimMapper()

    repository = CrudUdm(
        resource_type=resource_type,
        scim2udm_mapper=scim2udm_mapper,
        udm2scim_mapper=udm2scim_mapper,
        resource_class=resource_class,
        udm_url=udm_url,
        udm_username=udm_username,
        udm_password=udm_password,
    )

    return CrudManager(repository, resource_type)


@pytest.fixture(scope="session")
def directory_importer_config() -> Any:
    class ConnectorConfig:
        class UdmConfig:
            def __init__(self) -> None:
                self.uri = os.environ.get("UDM_URL", "http://localhost:9979/univention/udm/")
                self.user = os.environ.get("UDM_USERNAME", "admin")
                self.password = os.environ.get("UDM_PASSWORD", "univention")

        def __init__(self) -> None:
            self.udm = self.UdmConfig()

    return ConnectorConfig()


@pytest.fixture(scope="session")
def maildomain(directory_importer_config: Any) -> Any:
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


fake = Faker()


@pytest.fixture
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


@pytest.fixture
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
def test_user(random_user_data: dict[str, str]) -> User:
    """Create a test user with random data"""
    user = User(
        id=fake.uuid4(),
        schemas=[
            "urn:ietf:params:scim:schemas:core:2.0:User",
        ],
        user_name=random_user_data["username"],
        name=Name(given_name=random_user_data["given_name"], family_name=random_user_data["family_name"]),
        password="securepassword",
        display_name=f"{random_user_data['given_name']} {random_user_data['family_name']}",
        title="Senior Engineer",
        emails=[
            Email(value=random_user_data["email"], primary=True, type="work"),
            Email(value=random_user_data["personal_email"], type="home"),
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
            )
        ],
        active=True,
        preferred_language="en-US",
        user_type="employee",
    )

    return user


@pytest.fixture
async def user_fixture(test_user: User) -> AsyncGenerator[User, None]:
    """Create a user fixture with proper cleanup"""
    udm_url = os.environ.get("UDM_URL", "http://localhost:9979/univention/udm")
    udm_username = os.environ.get("UDM_USERNAME", "admin")
    udm_password = os.environ.get("UDM_PASSWORD", "univention")

    scim2udm_mapper = ScimToUdmMapper()
    udm2scim_mapper = UdmToScimMapper()

    udm_client = UDM.http(udm_url, udm_username, udm_password)

    # First, make sure there's no existing user with the same username
    await ensure_user_deleted(udm_client, username=test_user.user_name)

    # Create new user
    module = udm_client.get("users/user")
    udm_obj = module.new()

    for key, value in scim2udm_mapper.map_user(test_user).items():
        udm_obj.properties[key] = value

    udm_obj.save()

    created_user = udm2scim_mapper.map_user(udm_obj, base_url=udm_url)

    user_crud_manager = create_crud_manager("User", User, udm_url, udm_username, udm_password)
    user_service = UserServiceImpl(user_crud_manager)

    # Override the container's user_service for the duration of the test
    with ApplicationContainer.user_service.override(user_service):
        yield created_user

    # Cleanup - delete the user
    try:
        await ensure_user_deleted(udm_client, user_id=created_user.id)
    except Exception as e:
        print(f"Error cleaning up test user: {e}")


@pytest.fixture
def test_group(random_group_data: dict[str, str]) -> Group:
    """Create a test group with random data"""
    return Group(
        id=fake.uuid4(),
        schemas=["urn:ietf:params:scim:schemas:core:2.0:Group"],
        display_name=random_group_data["display_name"],
    )


@pytest.fixture
async def group_fixture(test_group: Group) -> AsyncGenerator[Group, None]:
    """Create a group fixture with proper cleanup"""
    udm_url = os.environ.get("UDM_URL", "http://localhost:9979/univention/udm")
    udm_username = os.environ.get("UDM_USERNAME", "admin")
    udm_password = os.environ.get("UDM_PASSWORD", "univention")

    scim2udm_mapper = ScimToUdmMapper()
    udm2scim_mapper = UdmToScimMapper()

    udm_client = UDM.http(udm_url, udm_username, udm_password)

    # First, make sure there's no existing group with the same name
    await ensure_group_deleted(udm_client, group_name=test_group.display_name)

    # Create new group
    module = udm_client.get("groups/group")
    udm_obj = module.new()

    group_properties = scim2udm_mapper.map_group(test_group)
    for key, value in group_properties.items():
        udm_obj.properties[key] = value

    udm_obj.save()

    created_group = udm2scim_mapper.map_group(udm_obj, base_url=udm_url)

    group_crud_manager = create_crud_manager("Group", Group, udm_url, udm_username, udm_password)
    group_service = GroupServiceImpl(group_crud_manager)

    # Override the container's group_service for the duration of the test
    with ApplicationContainer.group_service.override(group_service):
        yield created_group

    # Cleanup - delete the group
    try:
        await ensure_group_deleted(udm_client, group_id=created_group.id)
    except Exception as e:
        print(f"Error cleaning up test group: {e}")
