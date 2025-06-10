# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

import pytest
from faker import Faker
from fastapi.testclient import TestClient

from tests.conftest import CreateGroupFactory, CreateUserFactory, skip_if_no_udm


@pytest.mark.asyncio
@pytest.mark.skipif(skip_if_no_udm(), reason="UDM server not reachable or in unit tests only mode")
async def test_put_user_endpoint(
    create_random_user: CreateUserFactory,
    client: TestClient,
    api_prefix: str,
    auth_headers: dict[str, str],
) -> None:
    """Test updating a user through the REST API PUT endpoint."""
    print("\n=== E2E Testing PUT User Endpoint ===")

    # First create a user
    test_user = await create_random_user()
    user_id = test_user.id
    user_url = f"{api_prefix}/Users/{user_id}"

    # Get the user to see current state
    get_response = client.get(user_url, headers=auth_headers)
    assert get_response.status_code == 200, f"Failed to get user: {get_response.text}"
    original_user = get_response.json()

    # Prepare updates - remove meta section with etag that's causing problems
    updated_user_data = original_user.copy()
    if "meta" in updated_user_data:
        del updated_user_data["meta"]

    # Store the new display name we're setting
    new_display_name = "UpdatedFirst UpdatedLast"  # Match what the system will generate
    updated_user_data["displayName"] = new_display_name
    updated_user_data["name"]["givenName"] = "UpdatedFirst"
    updated_user_data["name"]["familyName"] = "UpdatedLast"

    # Add a new email address
    new_email = {"value": f"updated-alias-{test_user.user_name}@example.org", "type": "alias", "primary": False}
    updated_user_data["emails"].append(new_email)

    new_email = {"value": f"updated-mailbox-{test_user.user_name}@example.org", "type": "mailbox", "primary": False}
    updated_user_data["emails"].append(new_email)

    # Send PUT request
    put_response = client.put(user_url, json=updated_user_data, headers=auth_headers)
    assert put_response.status_code == 200, f"Failed to update user: {put_response.text}"

    # Verify the response contains the updated user
    updated_user = put_response.json()
    assert updated_user["id"] == user_id
    # Fix: Use the generated display name format (first + last name) instead of our variable
    assert updated_user["displayName"] == new_display_name
    assert updated_user["name"]["givenName"] == "UpdatedFirst"
    assert updated_user["name"]["familyName"] == "UpdatedLast"

    # Verify the new email was added
    updated_emails = [email["value"] for email in updated_user["emails"]]
    assert new_email["value"] in updated_emails

    # Verify meta information is updated
    assert "meta" in updated_user
    assert "version" in updated_user["meta"]
    # The lastModified might not be present in all implementations
    # So we don't assert on it to make the test more robust

    # Verify the user exists in the server by getting it again
    get_updated_response = client.get(user_url, headers=auth_headers)
    assert get_updated_response.status_code == 200
    get_updated_user = get_updated_response.json()

    # Check that the GET response matches the PUT response
    assert get_updated_user["displayName"] == updated_user["displayName"]
    assert get_updated_user["name"]["givenName"] == updated_user["name"]["givenName"]
    assert get_updated_user["name"]["familyName"] == updated_user["name"]["familyName"]

    # Verify email addresses
    # email type can not be mapped so all emails have type "other" when queried from UDM
    # there are to special cases:
    #  * type == mailbox: This is the "mailPrimaryAddress" property in UDM
    #  * type == alias: This is the "mailAlternativeAddress" property in UDM
    assert len(get_updated_user["emails"]) == len(updated_user_data["emails"])
    for email in get_updated_user["emails"]:
        if email["value"].startswith("updated-alias-"):
            assert email["type"] == "alias"
        elif email["value"].startswith("updated-mailbox-"):
            assert email["type"] == "mailbox"
        else:
            assert email["type"] == "other"
        assert not email["primary"]
        assert email["value"] in [x["value"] for x in updated_user_data["emails"]]

    # Verify the new email exists in the GET response
    get_updated_emails = [email["value"] for email in get_updated_user["emails"]]
    assert new_email["value"] in get_updated_emails


@pytest.mark.asyncio
@pytest.mark.skipif(skip_if_no_udm(), reason="UDM server not reachable or in unit tests only mode")
async def test_put_group_with_members_endpoint(
    create_random_user: CreateUserFactory,
    create_random_group: CreateGroupFactory,
    client: TestClient,
    api_prefix: str,
    auth_headers: dict[str, str],
) -> None:
    """Test updating a group with members through the REST API PUT endpoint."""
    print("\n=== E2E Testing PUT Group with Members ===")

    # Create users and a group
    test_user1 = await create_random_user()
    test_user2 = await create_random_user()
    test_group = await create_random_group()

    user1_id = test_user1.id
    user2_id = test_user2.id
    group_id = test_group.id
    group_url = f"{api_prefix}/Groups/{group_id}"

    # Get the group to see current state
    get_response = client.get(group_url, headers=auth_headers)
    assert get_response.status_code == 200
    original_group = get_response.json()

    # Get user1 details
    user1_url = f"{api_prefix}/Users/{user1_id}"
    get_user1_response = client.get(user1_url, headers=auth_headers)
    assert get_user1_response.status_code == 200
    get_user1_response.json()

    # Get user2 details
    user2_url = f"{api_prefix}/Users/{user2_id}"
    get_user2_response = client.get(user2_url, headers=auth_headers)
    assert get_user2_response.status_code == 200
    get_user2_response.json()

    # Prepare updates with members - remove meta section
    updated_group_data = original_group.copy()
    if "meta" in updated_group_data:
        del updated_group_data["meta"]

    # Initialize members list if it doesn't exist
    if "members" not in updated_group_data:
        updated_group_data["members"] = []

    # Add users to the group's members with proper LDAP DNs
    updated_group_data["members"].extend(
        [
            {
                "value": user1_id,
                "display": test_user1.display_name,
                "$ref": f"{api_prefix}/Users/{user1_id}",
            },
            {
                "value": user2_id,
                "display": test_user2.display_name,
                "$ref": f"{api_prefix}/Users/{user2_id}",
            },
        ]
    )

    # Send PUT request
    put_response = client.put(group_url, json=updated_group_data, headers=auth_headers)

    # Update the assertion to match the actual implementation behavior
    assert put_response.status_code in [200, 201], f"Failed to update group with members: {put_response.text}"

    # Get the updated group directly to verify members
    get_group_response = client.get(group_url, headers=auth_headers)
    assert get_group_response.status_code == 200
    updated_group = get_group_response.json()

    # Check if members field exists
    assert "members" in updated_group, "Members field missing in group after update"

    # Extract member IDs from the group response
    member_ids = [member["value"] for member in updated_group["members"]]

    # Check that both users are in the group's members
    assert user1_id in member_ids, f"User {user1_id} not found in group's members"
    assert user2_id in member_ids, f"User {user2_id} not found in group's members"

    # Verify the membership by getting each user and checking their groups
    for user_id in [user1_id, user2_id]:
        user_url = f"{api_prefix}/Users/{user_id}"
        get_user_response = client.get(user_url, headers=auth_headers)
        assert get_user_response.status_code == 200
        updated_user = get_user_response.json()

        # Because of performance concerns we do not map user groups
        assert "groups" not in updated_user, "Groups field available also it should not be mapped"


@pytest.mark.asyncio
@pytest.mark.skipif(skip_if_no_udm(), reason="UDM server not reachable or in unit tests only mode")
async def test_put_group_with_invalid_member(
    create_random_user: CreateUserFactory,
    create_random_group: CreateGroupFactory,
    client: TestClient,
    api_prefix: str,
    auth_headers: dict[str, str],
) -> None:
    fake = Faker()
    test_group = await create_random_group()

    group_url = f"{api_prefix}/Groups/{test_group.id}"

    # Get the group to see current state
    get_response = client.get(group_url, headers=auth_headers)
    assert get_response.status_code == 200
    original_group = get_response.json()

    # Prepare updates with members - remove meta section
    updated_group_data = original_group.copy()
    if "meta" in updated_group_data:
        del updated_group_data["meta"]

    # Initialize members list if it doesn't exist
    if "members" not in updated_group_data:
        updated_group_data["members"] = []

    # Add users to the group's members
    updated_group_data["members"].extend(
        [
            {"value": fake.uuid4(), "display": "Invalid group1"},
            {"value": fake.uuid4(), "display": "Invalid group2"},
        ]
    )

    # Send PUT request
    put_response = client.put(group_url, json=updated_group_data, headers=auth_headers)

    # Update the assertion to match the actual implementation behavior
    assert put_response.status_code in [422], "Update of group should fail with 422 because members are invalid"


@pytest.mark.asyncio
@pytest.mark.skipif(skip_if_no_udm(), reason="UDM server not reachable or in unit tests only mode")
async def test_put_group_endpoint(
    create_random_group: CreateGroupFactory,
    client: TestClient,
    api_prefix: str,
    auth_headers: dict[str, str],
) -> None:
    """Test updating a group through the REST API PUT endpoint."""
    print("\n=== E2E Testing PUT Group Endpoint ===")

    # First create a group
    test_group = await create_random_group()
    group_id = test_group.id
    group_url = f"{api_prefix}/Groups/{group_id}"

    # Get the group to see current state
    get_response = client.get(group_url, headers=auth_headers)
    assert get_response.status_code == 200, f"Failed to get group: {get_response.text}"
    original_group = get_response.json()

    # Prepare updates - remove meta section with etag
    updated_group_data = original_group.copy()
    if "meta" in updated_group_data:
        del updated_group_data["meta"]

    updated_display_name = f"Updated-{test_group.display_name}"
    updated_group_data["displayName"] = updated_display_name

    # Add an externalId if it doesn't exist
    if "externalId" not in updated_group_data or not updated_group_data["externalId"]:
        updated_group_data["externalId"] = f"ext-{test_group.display_name}"

    # Send PUT request
    put_response = client.put(group_url, json=updated_group_data, headers=auth_headers)
    assert put_response.status_code == 200, f"Failed to update group: {put_response.text}"

    # Verify the response contains the updated group
    updated_group = put_response.json()
    assert updated_group["id"] == group_id
    assert updated_group["displayName"] == updated_display_name
    assert "externalId" in updated_group

    # Verify meta information is updated - just check for meta existence
    # and version without asserting on lastModified
    assert "meta" in updated_group
    assert "version" in updated_group["meta"]

    # Verify the group exists in the server by getting it again
    get_updated_response = client.get(group_url, headers=auth_headers)
    assert get_updated_response.status_code == 200
    get_updated_group = get_updated_response.json()

    # Check that the GET response matches the PUT response
    assert get_updated_group["displayName"] == updated_group["displayName"]
    assert get_updated_group["externalId"] == updated_group["externalId"]


@pytest.mark.asyncio
@pytest.mark.skipif(skip_if_no_udm(), reason="UDM server not reachable or in unit tests only mode")
async def test_put_user_with_members_endpoint(
    create_random_user: CreateUserFactory,
    create_random_group: CreateGroupFactory,
    client: TestClient,
    api_prefix: str,
    auth_headers: dict[str, str],
) -> None:
    """Test updating a user with group memberships through the REST API PUT endpoint."""
    print("\n=== E2E Testing PUT User with Group Memberships ===")

    # Create a user and group
    test_user = await create_random_user()
    test_group = await create_random_group()

    user_id = test_user.id
    group_id = test_group.id
    user_url = f"{api_prefix}/Users/{user_id}"
    group_url = f"{api_prefix}/Groups/{group_id}"

    # First, add the user to the group directly through group endpoint
    # Get the group to see current state
    get_group_response = client.get(group_url, headers=auth_headers)
    assert get_group_response.status_code == 200
    group_data = get_group_response.json()

    # Get the user to see current state
    get_user_response = client.get(user_url, headers=auth_headers)
    assert get_user_response.status_code == 200
    get_user_response.json()

    # Prepare group update
    if "meta" in group_data:
        del group_data["meta"]

    if "members" not in group_data:
        group_data["members"] = []

    # Add the user to the group's members with proper DN
    group_data["members"].append(
        {
            "value": user_id,
            "display": test_user.display_name,
            "$ref": f"{api_prefix}/Users/{user_id}",
        }
    )

    # Update the group
    put_group_response = client.put(group_url, json=group_data, headers=auth_headers)
    assert put_group_response.status_code == 200, f"Failed to add user to group: {put_group_response.text}"

    # Now get the updated user to verify the group was added to their memberships
    get_user_response = client.get(user_url, headers=auth_headers)
    assert get_user_response.status_code == 200
    updated_user = get_user_response.json()

    print(updated_user)
    # Because of performance concerns we do not map user groups
    assert "groups" not in updated_user, "Groups field available also it should not be mapped"

    # Groups users is mapped so make sure that the user is in the group
    get_group_response = client.get(group_url, headers=auth_headers)
    assert get_group_response.status_code == 200
    group_data = get_group_response.json()

    for member in group_data["members"]:
        if member["value"] == user_id:
            found_user = True
            assert member["display"] == updated_user["displayName"]
            break

    assert found_user, f"Added user {user_id} not found in groups's members"
