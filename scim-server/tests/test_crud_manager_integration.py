# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH
import contextlib
import os
import socket
import urllib.parse
from collections.abc import AsyncGenerator

import pytest
from scim2_models import Email, Group, Name, User

from univention.scim.server.domain.group_service_impl import GroupServiceImpl
from univention.scim.server.domain.repo.container import RepositoryContainer
from univention.scim.server.domain.rules.display_name import UserDisplayNameRule
from univention.scim.server.domain.rules.evaluate import RuleEvaluator
from univention.scim.server.domain.user_service_impl import UserServiceImpl


def is_server_reachable(url: str, timeout: int = 2) -> bool:
    """Check if a server is reachable by making a connection to its host and port."""
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
    """Check if UDM URL is reachable or if unit test only mode is enabled."""
    # Check if we're in unit tests only mode
    if os.environ.get("UNIT_TESTS_ONLY") == "1":
        return True

    # Check if UDM URL is reachable
    udm_url = os.environ.get("UDM_URL", "http://localhost:9979/univention/udm")
    return not is_server_reachable(udm_url)


# Fixtures for test resources
@pytest.fixture
def test_user() -> User:
    """Create a test user."""
    return User(
        id="32a210b8-536c-4ad5-8339-a54fffbd9426",  # Use fixed ID for predictable tests
        schemas=["urn:ietf:params:scim:schemas:core:2.0:User"],
        user_name="jane.doe",
        name=Name(given_name="Jane", family_name="Doe"),
        emails=[Email(value="jane.doe@example.com", primary=True, type="work")],
        active=True,
    )


@pytest.fixture
def test_group() -> Group:
    """Create a test group."""
    return Group(
        id="a8b90015-cbbc-4579-aa37-ef363452ec9a",  # Use fixed ID for predictable tests
        schemas=["urn:ietf:params:scim:schemas:core:2.0:Group"],
        display_name="Engineering Team",
    )


@pytest.fixture
async def user_fixture(test_user: User) -> AsyncGenerator[User, None]:
    """Fixture that creates and then cleans up a user."""
    # Create a CrudManager for User resources
    user_crud_manager = RepositoryContainer.create_for_udm("User", User, "http://test.local", "test", "test")
    user_service = UserServiceImpl(user_crud_manager)

    # Create the user
    created_user = await user_service.create_user(test_user)

    # Yield the created user for test use
    yield created_user

    # Clean up after test
    with contextlib.suppress(Exception):
        await user_service.delete_user(created_user.id)


@pytest.fixture
async def group_fixture(test_group: Group) -> AsyncGenerator[Group, None]:
    """Fixture that creates and then cleans up a group."""
    # Create a CrudManager for Group resources
    group_crud_manager = RepositoryContainer.create_for_udm("Group", Group, "http://test.local", "test", "test")
    group_service = GroupServiceImpl(group_crud_manager)

    # Create the group
    created_group = await group_service.create_group(test_group)

    # Yield the created group for test use
    yield created_group

    # Clean up after test
    with contextlib.suppress(Exception):
        await group_service.delete_group(created_group.id)


@pytest.mark.asyncio
@pytest.mark.skipif(skip_if_no_udm(), reason="UDM server not reachable or in unit tests only mode")
async def test_user_service(user_fixture: User) -> None:
    """Test the UserService implementation with CrudManager."""
    print("\n=== Testing User Service ===")

    # Create a CrudManager for User resources
    user_crud_manager = RepositoryContainer.create_for_udm("User", User, "http://test.local", "test", "test")
    user_service = UserServiceImpl(user_crud_manager)

    # We already have a user created by the fixture
    created_user = user_fixture
    print(f"Using user with ID: {created_user.id}")
    print(f"Display name: {created_user.display_name}")

    # Retrieve the user
    print("\nRetrieving user...")
    retrieved_user = await user_service.get_user(created_user.id)
    print(f"Retrieved user: {retrieved_user.display_name}")

    # Update the user
    print("\nUpdating user...")
    retrieved_user.nick_name = "JD"
    updated_user = await user_service.update_user(retrieved_user.id, retrieved_user)
    print(f"Updated user nickname: {updated_user.nick_name}")

    # List users
    print("\nListing users...")
    users_response = await user_service.list_users()
    print(f"Total users: {users_response.total_results}")
    print(f"First user: {users_response.resources[0].display_name}")


@pytest.mark.asyncio
@pytest.mark.skipif(skip_if_no_udm(), reason="UDM server not reachable or in unit tests only mode")
async def test_group_service(group_fixture: Group) -> None:
    """Test the GroupService implementation with CrudManager."""
    print("\n=== Testing Group Service ===")

    # Create a CrudManager for Group resources
    group_crud_manager = RepositoryContainer.create_for_udm("Group", Group, "http://test.local", "test", "test")
    group_service = GroupServiceImpl(group_crud_manager)

    # We already have a group created by the fixture
    created_group = group_fixture
    print(f"Using group with ID: {created_group.id}")

    # Retrieve the group
    print("\nRetrieving group...")
    retrieved_group = await group_service.get_group(created_group.id)
    print(f"Retrieved group: {retrieved_group.display_name}")

    # Update the group
    print("\nUpdating group...")
    retrieved_group.display_name = "Engineering Department"
    updated_group = await group_service.update_group(retrieved_group.id, retrieved_group)
    print(f"Updated group name: {updated_group.display_name}")

    # List groups
    print("\nListing groups...")
    groups_response = await group_service.list_groups()
    print(f"Total groups: {groups_response.total_results}")
    print(f"First group: {groups_response.resources[0].display_name}")


@pytest.mark.asyncio
async def test_rule_application() -> None:
    """Test the application of rules to User resources."""
    print("\n=== Testing Rule Application ===")

    # Create a user without a display name
    user = User(user_name="john.smith", name=Name(given_name="John", family_name="Smith"))
    print(f"Original user: {user.display_name=}")

    # Create rule evaluator with display name rule
    rule_evaluator = RuleEvaluator[User]()
    rule_evaluator.add_rule(UserDisplayNameRule())

    # Apply rules
    updated_user = await rule_evaluator.evaluate(user)
    print(f"After rules: {updated_user.display_name=}")
    assert updated_user.display_name == "John Smith", "Display name rule failed"
