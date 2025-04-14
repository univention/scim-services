# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH
import contextlib
import os
import socket
import urllib.parse
from collections.abc import AsyncGenerator

import pytest
from scim2_models import Address, Email, Group, Name, PhoneNumber, User

from univention.scim.server.domain.group_service_impl import GroupServiceImpl
from univention.scim.server.domain.repo.container import RepositoryContainer
from univention.scim.server.domain.rules.display_name import UserDisplayNameRule
from univention.scim.server.domain.rules.evaluate import RuleEvaluator
from univention.scim.server.domain.user_service_impl import UserServiceImpl
from univention.scim.server.model_service.udm2scim import UdmToScimMapper


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
    user = User(
        id="32a210b8-536c-4ad5-8339-a54fffbd9426",  # Use fixed ID for predictable tests
        schemas=[
            "urn:ietf:params:scim:schemas:core:2.0:User",
        ],
        user_name="jane.doe",
        name=Name(given_name="Jane", family_name="Doe"),
        display_name="Jane Doe",
        title="Senior Engineer",
        emails=[
            Email(value="jane.doe@example.com", primary=True, type="work"),
            Email(value="jane.personal@example.com", type="home"),
        ],
        phone_numbers=[
            PhoneNumber(value="+1-555-123-4567", type="work"),
            PhoneNumber(value="+1-555-987-6543", type="mobile"),
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

    # Check for extended attributes in retrieved user
    if retrieved_user.emails:
        print(f"User has {len(retrieved_user.emails)} email(s)")
    if retrieved_user.phone_numbers:
        print(f"User has {len(retrieved_user.phone_numbers)} phone number(s)")
    if retrieved_user.addresses:
        print(f"User has {len(retrieved_user.addresses)} address(es)")

    # Check for enterprise extension
    enterprise_ext = getattr(retrieved_user, "urn:ietf:params:scim:schemas:extension:enterprise:2.0:User", None)
    if enterprise_ext:
        print("Enterprise extension found:")
        for key, value in enterprise_ext.items():
            print(f"  {key}: {value}")


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


@pytest.mark.asyncio
async def test_udm_to_scim_mapper() -> None:
    """Test the UDM to SCIM mapper with comprehensive attributes from the mapping table."""
    print("\n=== Testing UDM to SCIM Mapper ===")

    # Create a mock UDM user with attributes from our mapping table
    # This structure mimics the actual UDM REST API response format
    udm_user = {
        "dn": "uid=test.user,cn=users,dc=example,dc=com",
        "uri": "/univention/udm/users/user/test-uuid-1234",
        "props": {
            "univentionObjectIdentifier": "test-uuid-1234",
            "username": "test.user",
            "firstname": "Test",
            "lastname": "User",
            "displayName": "Test User",
            "title": "Test Engineer",
            "disabled": False,
            "createTimestamp": "20230101000000Z",
            "modifyTimestamp": "20230201000000Z",
            "mailPrimaryAddress": "test.user@example.com",
            "mailAlternativeAddress": ["alt.user@example.com", "another@example.com"],
            "phone": ["+1-555-111-2222"],
            "mobileTelephoneNumber": ["+1-555-333-4444"],
            "homeTelephoneNumber": ["+1-555-555-6666"],
            "pagerTelephoneNumber": ["+1-555-777-8888"],
            "street": "456 Test St",
            "city": "Test City",
            "postcode": "12345",
            "country": "Test Country",
            "preferredLanguage": "en",
            "employeeType": "contractor",
            # Enterprise attributes
            "employeeNumber": "E54321",
            "departmentNumber": ["QA", "Test"],
            "organisation": "Test Organization",
            "secretary": ["manager1", "manager2"],
            # Certificate attributes
            "userCertificate": "Q0VSVDY0MjQK",
            "certificateSubjectCommonName": "Test User Cert",
        },
        "position": "cn=users,dc=example,dc=com",
        "objectType": "users/user",
        "options": {"posix": True, "samba": True},
        "policies": {"policies/umc": ["cn=default-umc-policy,cn=policies,dc=example,dc=com"]},
    }

    # Create the mapper
    mapper = UdmToScimMapper()

    # Map the UDM user to SCIM
    base_url = "https://scim.example.com"
    scim_user = mapper.map_user(udm_user, base_url)

    # Verify core attributes
    print(f"Mapped user ID: {scim_user.id}")
    assert scim_user.id == "test-uuid-1234", "ID mapping failed"
    assert scim_user.user_name == "test.user", "Username mapping failed"
    assert scim_user.active is True, "Active status mapping failed"
    assert scim_user.display_name == "Test User", "Display name mapping failed"
    assert scim_user.title == "Test Engineer", "Title mapping failed"
    assert scim_user.preferred_language == "en", "Preferred language mapping failed"
    assert scim_user.user_type == "contractor", "User type mapping failed"

    # Verify metadata
    assert scim_user.meta.resource_type == "User", "Resource type mapping failed"
    assert scim_user.meta.location == f"{base_url}/Users/test-uuid-1234", "Location mapping failed"

    # Handle datetime or string format for timestamps
    created_str = (
        scim_user.meta.created.strftime("%Y-%m-%dT%H:%M:%SZ")
        if hasattr(scim_user.meta.created, "strftime")
        else scim_user.meta.created
    )
    assert created_str == "2023-01-01T00:00:00Z", "Created timestamp mapping failed"

    modified_str = (
        scim_user.meta.last_modified.strftime("%Y-%m-%dT%H:%M:%SZ")
        if hasattr(scim_user.meta.last_modified, "strftime")
        else scim_user.meta.last_modified
    )
    assert modified_str == "2023-02-01T00:00:00Z", "Modified timestamp mapping failed"

    # Verify name
    assert scim_user.name.given_name == "Test", "Given name mapping failed"
    assert scim_user.name.family_name == "User", "Family name mapping failed"
    assert scim_user.name.formatted == "Test User", "Formatted name mapping failed"

    # Verify emails
    assert len(scim_user.emails) == 3, "Email count mapping failed"
    assert any(e.value == "test.user@example.com" and e.primary for e in scim_user.emails), (
        "Primary email mapping failed"
    )
    assert any(e.value == "alt.user@example.com" for e in scim_user.emails), "Alternative email mapping failed"
    assert any(e.value == "another@example.com" for e in scim_user.emails), "Multiple alternative emails mapping failed"

    # Verify phone numbers
    assert len(scim_user.phone_numbers) == 4, "Phone number count mapping failed"
    assert any(p.value == "+1-555-111-2222" and p.type == "work" for p in scim_user.phone_numbers), (
        "Work phone mapping failed"
    )
    assert any(p.value == "+1-555-333-4444" and p.type == "mobile" for p in scim_user.phone_numbers), (
        "Mobile phone mapping failed"
    )
    assert any(p.value == "+1-555-555-6666" and p.type == "home" for p in scim_user.phone_numbers), (
        "Home phone mapping failed"
    )
    assert any(p.value == "+1-555-777-8888" and p.type == "pager" for p in scim_user.phone_numbers), (
        "Pager mapping failed"
    )

    # Verify address
    assert len(scim_user.addresses) == 1, "Address count mapping failed"
    assert scim_user.addresses[0].street_address == "456 Test St", "Street address mapping failed"
    assert scim_user.addresses[0].locality == "Test City", "City mapping failed"
    assert scim_user.addresses[0].postal_code == "12345", "Postal code mapping failed"
    assert scim_user.addresses[0].country == "Test Country", "Country mapping failed"

    # Verify certificates
    assert len(scim_user.x509_certificates) == 1, "Certificate count mapping failed"
    assert scim_user.x509_certificates[0].value
    assert scim_user.x509_certificates[0].display == "Test User Cert", "Certificate display mapping failed"

    # Not testing the enterprise extension as this functionality has been removed
    print("Enterprise extension: Disabled")


@pytest.mark.asyncio
async def test_udm_to_scim_mapper_edge_cases() -> None:
    """Test the UDM to SCIM mapper with edge cases and missing data."""
    print("\n=== Testing UDM to SCIM Mapper Edge Cases ===")

    # Create a minimal UDM user with only required fields
    minimal_udm_user = {
        "dn": "uid=minimal.user,cn=users,dc=example,dc=com",
        "props": {
            "username": "minimal.user",
            # Include a non-standard timestamp format to test robustness
            "createTimestamp": "2023-01-15T12:30:45Z",
            # No other fields provided
        },
    }

    # Create the mapper
    mapper = UdmToScimMapper()

    # Map the minimal UDM user to SCIM
    scim_user = mapper.map_user(minimal_udm_user)

    # Verify basic mapping still works
    assert scim_user.user_name == "minimal.user", "Username mapping failed for minimal user"
    assert scim_user.id == "minimal.user", "ID fallback to username failed"
    assert scim_user.active is True, "Active default status failed"
    # Verify timestamp is properly handled
    assert scim_user.meta.created is not None, "Timestamp handling failed"
    # Allow for either string or datetime type in timestamp
    timestamp_str = (
        scim_user.meta.created
        if isinstance(scim_user.meta.created, str)
        else scim_user.meta.created.strftime("%Y-%m-%dT%H:%M:%SZ")
    )
    assert timestamp_str == "2023-01-15T12:30:45Z", "ISO timestamp handling failed"

    # Test with empty props
    empty_props_user = {"dn": "uid=empty.user,cn=users,dc=example,dc=com", "props": {}}

    empty_user = mapper.map_user(empty_props_user)
    assert empty_user.id == "unknown", "Default ID handling failed"

    # Test with malformed email list
    malformed_email_user = {
        "dn": "uid=malformed.user,cn=users,dc=example,dc=com",
        "props": {
            "username": "malformed.user",
            "mailAlternativeAddress": "not.a.list@example.com",  # String instead of list
        },
    }

    email_user = mapper.map_user(malformed_email_user)
    assert len(email_user.emails) == 1, "Malformed email list handling failed"
    assert email_user.emails[0].value == "not.a.list@example.com", "Single string email conversion failed"
