# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

import os
import random
import socket
import urllib.parse
from collections.abc import AsyncGenerator
from typing import Any

import pytest
import requests
from faker import Faker
from scim2_models import Address, Email, Group, Name, User
from univention.admin.rest.client import UDM

from univention.scim.server.domain.group_service_impl import GroupServiceImpl
from univention.scim.server.domain.repo.crud_manager import CrudManager
from univention.scim.server.domain.repo.udm.crud_udm import CrudUdm
from univention.scim.server.domain.rules.display_name import UserDisplayNameRule
from univention.scim.server.domain.rules.evaluate import RuleEvaluator
from univention.scim.server.domain.user_service_impl import UserServiceImpl
from univention.scim.server.model_service.scim2udm import ScimToUdmMapper
from univention.scim.server.model_service.udm2scim import UdmToScimMapper


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


@pytest.fixture(scope="session", autouse=True)
def maildomain(directory_importer_config: Any) -> Any:
    base_url = f"{directory_importer_config.udm.uri}mail/domain/"
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


def skip_if_no_udm() -> bool:
    if os.environ.get("UNIT_TESTS_ONLY") == "1":
        return True

    udm_url = os.environ.get("UDM_URL", "http://localhost:9979/univention/udm")
    return not is_server_reachable(udm_url)


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
                print(f"Deleting existing user: {udm_obj.properties.username}")
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
                print(f"Deleting existing group: {udm_obj.properties.name}")
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
def test_group(random_group_data: dict[str, str]) -> Group:
    """Create a test group with random data"""
    return Group(
        id=fake.uuid4(),
        schemas=["urn:ietf:params:scim:schemas:core:2.0:Group"],
        display_name=random_group_data["display_name"],
    )


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
    UserServiceImpl(user_crud_manager)

    yield created_user

    # Cleanup - delete the user
    try:
        await ensure_user_deleted(udm_client, user_id=created_user.id)
    except Exception as e:
        print(f"Error cleaning up test user: {e}")


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
    GroupServiceImpl(group_crud_manager)

    yield created_group

    # Cleanup - delete the group
    try:
        await ensure_group_deleted(udm_client, group_id=created_group.id)
    except Exception as e:
        print(f"Error cleaning up test group: {e}")


@pytest.mark.asyncio
@pytest.mark.skipif(skip_if_no_udm(), reason="UDM server not reachable or in unit tests only mode")
async def test_user_service(user_fixture: User) -> None:
    print("\n=== Testing User Service ===")

    udm_url = os.environ.get("UDM_URL", "http://localhost:9979/univention/udm")
    udm_username = os.environ.get("UDM_USERNAME", "admin")
    udm_password = os.environ.get("UDM_PASSWORD", "univention")

    ScimToUdmMapper()
    udm2scim_mapper = UdmToScimMapper()

    udm_client = UDM.http(udm_url, udm_username, udm_password)

    user_crud_manager = create_crud_manager("User", User, udm_url, udm_username, udm_password)
    UserServiceImpl(user_crud_manager)

    created_user = user_fixture
    print(f"Using user with ID: {created_user.id}")
    print(f"Display name: {created_user.display_name}")

    print("\nRetrieving user with UDM client...")
    module = udm_client.get("users/user")
    filter_str = f"univentionObjectIdentifier={created_user.id}"
    results = list(module.search(filter_str))

    assert results, f"User with ID {created_user.id} not found"
    udm_obj = results[0].open()
    retrieved_user = udm2scim_mapper.map_user(udm_obj, base_url=udm_url)
    print(f"Retrieved user: {retrieved_user.display_name}")

    assert retrieved_user == created_user


@pytest.mark.asyncio
@pytest.mark.skipif(skip_if_no_udm(), reason="UDM server not reachable or in unit tests only mode")
async def test_group_service(group_fixture: Group) -> None:
    print("\n=== Testing Group Service ===")

    udm_url = os.environ.get("UDM_URL", "http://localhost:9979/univention/udm")
    udm_username = os.environ.get("UDM_USERNAME", "admin")
    udm_password = os.environ.get("UDM_PASSWORD", "univention")

    ScimToUdmMapper()
    UdmToScimMapper()

    udm_client = UDM.http(udm_url, udm_username, udm_password)

    group_crud_manager = create_crud_manager("Group", Group, udm_url, udm_username, udm_password)
    GroupServiceImpl(group_crud_manager)

    created_group = group_fixture
    print(f"Using group with ID: {created_group.id}")

    print("\nRetrieving group with UDM client...")
    module = udm_client.get("groups/group")
    filter_str = f"univentionObjectIdentifier={created_group.id}"
    results = list(module.search(filter_str))

    assert results, f"Group with ID {created_group.id} not found"
    results[0].open()
    udm_object = results[0].open()
    retrieved_group = UdmToScimMapper().map_group(udm_object, base_url=udm_url)
    print(f"Retrieved group: {retrieved_group.display_name}")

    assert retrieved_group == created_group


@pytest.mark.asyncio
async def test_rule_application() -> None:
    print("\n=== Testing Rule Application ===")

    user = User(user_name="john.smith", name=Name(given_name="John", family_name="Smith"))
    print(f"Original user: {user.display_name=}")

    rule_evaluator = RuleEvaluator[User]()
    rule_evaluator.add_rule(UserDisplayNameRule())

    updated_user = await rule_evaluator.evaluate(user)
    print(f"After rules: {updated_user.display_name=}")
    assert updated_user.display_name == "John Smith", "Display name rule failed"
