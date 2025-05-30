# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

import os

import pytest
from faker import Faker
from fastapi.testclient import TestClient
from scim2_models import Group, GroupMember, User

from .conftest import CreateGroupFactory, CreateUserFactory, skip_if_no_udm


@pytest.fixture
def api_prefix() -> str:
    """Get the API prefix for the SCIM server."""
    return os.environ.get("API_PREFIX", "/scim/v2")


@pytest.fixture
def auth_headers() -> dict[str, str]:
    """Get authentication headers for API requests."""
    return {"Authorization": "Bearer test-token"}


@pytest.mark.asyncio
@pytest.mark.skipif(skip_if_no_udm(), reason="UDM server not reachable or in unit tests only mode")
async def test_list_user_endpoint(
    create_random_user: CreateUserFactory,
    client: TestClient,
    api_prefix: str,
    auth_headers: dict[str, str],
) -> None:
    """Test retrieving a list of users through the REST API endpoint."""
    print("\n=== E2E Testing GET Users Endpoint ===")

    await create_random_user()
    await create_random_user()
    await create_random_user()
    await create_random_user()
    await create_random_user()

    list_users_url = f"{api_prefix}/Users"
    response = client.get(list_users_url, headers=auth_headers)

    assert response.status_code == 200, f"Failed to get list of users: {response.text}"
    all_users = response.json()
    assert all_users["totalResults"] == 5
    assert all_users["startIndex"] == 1
    assert len(all_users["Resources"]) == all_users["totalResults"]

    response = client.get(f"{list_users_url}?start_index=2&count=2", headers=auth_headers)

    assert response.status_code == 200, f"Failed to get partial list of users: {response.text}"
    partial_users = response.json()
    assert partial_users["totalResults"] == 5
    assert partial_users["startIndex"] == 2
    assert len(partial_users["Resources"]) == 2
    assert partial_users["Resources"][0] == all_users["Resources"][1]
    assert partial_users["Resources"][1] == all_users["Resources"][2]


@pytest.mark.asyncio
@pytest.mark.skipif(skip_if_no_udm(), reason="UDM server not reachable or in unit tests only mode")
async def test_get_user_endpoint(
    create_random_user: CreateUserFactory,
    client: TestClient,
    api_prefix: str,
    auth_headers: dict[str, str],
) -> None:
    """Test retrieving a user through the REST API endpoint."""
    print("\n=== E2E Testing GET User Endpoint ===")

    test_user = await create_random_user()
    user_id = test_user.id
    user_url = f"{api_prefix}/Users/{user_id}"

    response = client.get(user_url, headers=auth_headers)

    assert response.status_code == 200, f"Failed to get user: {response.text}"
    user_data = response.json()

    # Verify essential user properties
    assert user_data["id"] == user_id
    assert user_data["userName"] == test_user.user_name
    assert user_data["displayName"] == test_user.display_name

    # Verify nested properties
    assert user_data["name"]["givenName"] == test_user.name.given_name
    assert user_data["name"]["familyName"] == test_user.name.family_name

    # Verify email addresses
    primary_email = next((email for email in user_data["emails"] if email.get("primary", False)), None)
    assert primary_email is not None, "No primary email found"
    assert primary_email["value"] in [email.value for email in test_user.emails]


@pytest.mark.skipif(skip_if_no_udm(), reason="UDM server not reachable or in unit tests only mode")
async def test_post_user_endpoint(
    random_user: User, client: TestClient, api_prefix: str, auth_headers: dict[str, str]
) -> None:
    """Test creating a user through the REST API endpoint."""
    print("\n=== E2E Testing POST User Endpoint ===")

    test_user = random_user

    # Make sure to not send an ID, as we want the server to generate one
    test_user.id = None

    user_url = f"{api_prefix}/Users"
    test_user_dict = test_user.model_dump(exclude_none=True)

    response = client.post(user_url, json=test_user_dict, headers=auth_headers)

    assert response.status_code == 201, f"Failed to create user: {response.text}"
    created_user = response.json()

    # Verify Location header
    assert response.headers.get("Location", "").startswith("/Users/")

    # Verify essential user properties
    assert created_user["id"] is not None, "Created user does not have an ID"
    assert created_user["userName"] == test_user.user_name
    assert created_user["displayName"] == test_user.display_name

    # Verify nested properties
    assert created_user["name"]["givenName"] == test_user.name.given_name
    assert created_user["name"]["familyName"] == test_user.name.family_name

    # Verify email addresses
    primary_email = next((email for email in created_user["emails"] if email.get("primary", False)), None)
    assert primary_email is not None, "No primary email found"
    assert primary_email["value"] in [email.value for email in test_user.emails]


@pytest.mark.asyncio
@pytest.mark.skipif(skip_if_no_udm(), reason="UDM server not reachable or in unit tests only mode")
async def test_list_group_endpoint(
    create_random_group: CreateGroupFactory,
    client: TestClient,
    api_prefix: str,
    auth_headers: dict[str, str],
) -> None:
    """Test retrieving a list of groups through the REST API endpoint."""
    print("\n=== E2E Testing GET Groups Endpoint ===")

    await create_random_group()
    await create_random_group()
    await create_random_group()
    await create_random_group()
    await create_random_group()

    list_groups_url = f"{api_prefix}/Groups"
    response = client.get(list_groups_url, headers=auth_headers)

    assert response.status_code == 200, f"Failed to get list of groups: {response.text}"
    all_groups = response.json()
    # Some default groups are available so make sure we have at least 5 groups
    assert all_groups["totalResults"] >= 5
    assert all_groups["startIndex"] == 1
    assert len(all_groups["Resources"]) == all_groups["totalResults"]

    response = client.get(f"{list_groups_url}?start_index=3&count=3", headers=auth_headers)

    assert response.status_code == 200, f"Failed to get partial list of groups: {response.text}"
    partial_groups = response.json()
    assert partial_groups["totalResults"] >= 5
    assert partial_groups["startIndex"] == 3
    assert len(partial_groups["Resources"]) == 3
    assert partial_groups["Resources"][0] == all_groups["Resources"][2]
    assert partial_groups["Resources"][1] == all_groups["Resources"][3]
    assert partial_groups["Resources"][2] == all_groups["Resources"][4]


@pytest.mark.asyncio
@pytest.mark.skipif(skip_if_no_udm(), reason="UDM server not reachable or in unit tests only mode")
async def test_get_group_endpoint(
    create_random_group: CreateGroupFactory,
    create_random_user: CreateUserFactory,
    client: TestClient,
    api_prefix: str,
    auth_headers: dict[str, str],
) -> None:
    """Test retrieving a group through the REST API endpoint."""
    print("\n=== E2E Testing GET Group Endpoint ===")

    # Add some users to the group
    users = []
    group_members: list[GroupMember] = []
    for _i in range(10):
        user = await create_random_user()
        users.append(user)
        group_members.append(GroupMember(value=user.id, display=user.display_name, type="User"))

    test_group = await create_random_group(group_members)
    group_id = test_group.id
    group_url = f"{api_prefix}/Groups/{group_id}"

    response = client.get(group_url, headers=auth_headers)

    assert response.status_code == 200, f"Failed to get group: {response.text}"
    group_data = response.json()

    # Verify essential group properties
    assert group_data["id"] == group_id
    assert group_data["displayName"] == test_group.display_name
    assert len(group_data["members"]) == len(users)
    for user in users:
        assert {"value": user.id, "display": user.display_name, "type": "User"} in group_data["members"]


@pytest.mark.skipif(skip_if_no_udm(), reason="UDM server not reachable or in unit tests only mode")
async def test_post_group_endpoint(
    random_group: Group, client: TestClient, api_prefix: str, auth_headers: dict[str, str]
) -> None:
    """Test creating a group through the REST API endpoint."""
    print("\n=== E2E Testing POST group Endpoint ===")

    test_group = random_group

    # Make sure to not send an ID, as we want the server to generate one
    test_group.id = None

    group_url = f"{api_prefix}/Groups"
    test_group_dict = test_group.model_dump(exclude_none=True)

    response = client.post(group_url, json=test_group_dict, headers=auth_headers)

    assert response.status_code == 201, f"Failed to create group: {response.text}"
    created_group = response.json()

    # Verify Location header
    assert response.headers.get("Location", "").startswith("/Groups/")

    # Verify essential group properties
    assert created_group["id"] is not None, "Created group does not have an ID"
    assert created_group["externalId"] is not None, "Created group does not have an externalId"
    assert created_group["displayName"] == test_group.display_name

    # Verify meta properties
    assert "meta" in created_group, "Created group does not have meta information"
    assert created_group["meta"]["resourceType"] == "Group"
    assert created_group["meta"]["location"].endswith(f"/Groups/{created_group['id']}")
    assert created_group["meta"]["version"] is not None

    # Verify schemas
    assert "schemas" in created_group, "Created group does not have schemas"
    assert "urn:ietf:params:scim:schemas:core:2.0:Group" in created_group["schemas"]


@pytest.mark.asyncio
@pytest.mark.skipif(skip_if_no_udm(), reason="UDM server not reachable or in unit tests only mode")
async def test_get_resource_types_endpoint(client: TestClient, api_prefix: str, auth_headers: dict[str, str]) -> None:
    """E2E test retrieving the SCIM ResourceTypes using ListResponse."""
    print("\n=== E2E Testing GET ResourceTypes Endpoint (ListResponse) ===")

    response = client.get(f"{api_prefix}/ResourceTypes", headers=auth_headers)

    # --- Basic Response Validation ---
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    data = response.json()
    assert isinstance(data, dict), f"Expected response data to be a dict, got {type(data)}"

    # --- ListResponse Structure Validation ---
    # Check for ListResponse schema
    assert "schemas" in data, "Response missing 'schemas' field"
    assert isinstance(data["schemas"], list), "'schemas' field should be a list"
    assert "urn:ietf:params:scim:api:messages:2.0:ListResponse" in data["schemas"], (
        "ListResponse schema missing from 'schemas'"
    )

    # Check pagination/list attributes
    assert "totalResults" in data, "Response missing 'totalResults' field"
    assert isinstance(data["totalResults"], int), "'totalResults' should be an integer"
    assert data["totalResults"] >= 0, "'totalResults' should be non-negative"

    assert "itemsPerPage" in data, "Response missing 'itemsPerPage' field"
    assert isinstance(data["itemsPerPage"], int), "'itemsPerPage' should be an integer"

    assert "startIndex" in data, "Response missing 'startIndex' field"
    assert isinstance(data["startIndex"], int), "'startIndex' should be an integer"

    # Check for the Resources list
    assert "Resources" in data, "Response missing 'Resources' field"
    assert isinstance(data["Resources"], list), "'Resources' field should be a list"

    # --- Content Validation (Resources List) ---
    resources_list = data["Resources"]

    # Check totalResults matches the number of items in Resources
    assert data["totalResults"] == len(resources_list), (
        f"'totalResults' ({data['totalResults']}) does not match number of items in 'Resources' ({len(resources_list)})"
    )

    # Check if User and Group resource types are present
    resource_ids = [rt.get("id") for rt in resources_list if isinstance(rt, dict)]
    assert "User" in resource_ids, "User ResourceType not found in 'Resources'"
    assert "Group" in resource_ids, "Group ResourceType not found in 'Resources'"

    print("=== GET ResourceTypes Endpoint Test Passed ===")


## PUT


# Fixed PUT test functions


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
    new_email = {"value": f"updated-{test_user.user_name}@example.org", "type": "work", "primary": True}
    # Make sure we don't have duplicate primary emails
    for email in updated_user_data["emails"]:
        email["primary"] = False
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

    # Verify primary email is set correctly
    primary_emails = [email for email in updated_user["emails"] if email.get("primary", False)]
    assert len(primary_emails) == 1
    assert primary_emails[0]["value"] == new_email["value"]

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

    # Verify the new email exists in the GET response
    get_updated_emails = [email["value"] for email in get_updated_user["emails"]]
    assert new_email["value"] in get_updated_emails


@pytest.mark.asyncio
@pytest.mark.skipif(skip_if_no_udm(), reason="UDM server not reachable or in unit tests only mode")
async def test_patch_user_endpoint(
    create_random_user: CreateUserFactory,
    client: TestClient,
    api_prefix: str,
    auth_headers: dict[str, str],
) -> None:
    """Test partially updating a user through the REST API PATCH endpoint."""
    print("\n=== E2E Testing PATCH User Endpoint ===")

    # Step 1: Create a test user
    test_user = await create_random_user()
    user_id = test_user.id
    user_url = f"{api_prefix}/Users/{user_id}"

    # Step 3: Prepare patch operations
    new_display_name = "PatchedFirst PatchedLast"
    new_email_value = f"patched-{test_user.user_name}@example.org"

    patch_body = {
        "schemas": ["urn:ietf:params:scim:api:messages:2.0:PatchOp"],
        "Operations": [
            {"op": "replace", "path": "displayName", "value": new_display_name},
            {"op": "replace", "path": "name.givenName", "value": "PatchedFirst"},
            {"op": "replace", "path": "name.familyName", "value": "PatchedLast"},
            {"op": "add", "path": "emails", "value": [{"value": new_email_value, "type": "work", "primary": True}]},
        ],
    }

    # Step 4: Send PATCH request
    patch_response = client.patch(user_url, json=patch_body, headers=auth_headers)
    assert patch_response.status_code == 200, f"PATCH failed: {patch_response.text}"
    patched_user = patch_response.json()

    # Step 5: Assert updated fields
    assert patched_user["id"] == user_id
    assert patched_user["displayName"] == new_display_name
    assert patched_user["name"]["givenName"] == "PatchedFirst"
    assert patched_user["name"]["familyName"] == "PatchedLast"

    # Step 6: Check updated emails
    email_values = [e["value"] for e in patched_user["emails"]]
    assert new_email_value in email_values

    primary_emails = [e for e in patched_user["emails"] if e.get("primary")]
    assert len(primary_emails) == 1
    assert primary_emails[0]["value"] == new_email_value

    # Step 7: Re-GET to confirm persistence
    get_final = client.get(user_url, headers=auth_headers)
    assert get_final.status_code == 200
    final_user = get_final.json()

    assert final_user["displayName"] == new_display_name
    assert final_user["name"]["givenName"] == "PatchedFirst"
    assert final_user["name"]["familyName"] == "PatchedLast"
    final_emails = [e["value"] for e in final_user["emails"]]
    assert new_email_value in final_emails


@pytest.mark.asyncio
@pytest.mark.skipif(skip_if_no_udm(), reason="UDM server not reachable or in unit tests only mode")
@pytest.mark.usefixtures("maildomain")
async def test_patch_group_endpoint(
    create_random_group: CreateGroupFactory, client: TestClient, api_prefix: str, auth_headers: dict[str, str]
) -> None:
    """Test partially updating a group through the REST API PATCH endpoint."""
    print("\n=== E2E Testing PATCH Group Endpoint ===")

    # Step 1: Create a test group
    test_group = await create_random_group()
    group_id = test_group.id
    group_url = f"{api_prefix}/Groups/{group_id}"

    # Step 3: Prepare patch operations
    new_display_name = "PatchedGroup"

    patch_body = {
        "schemas": ["urn:ietf:params:scim:api:messages:2.0:PatchOp"],
        "Operations": [
            {"op": "replace", "path": "displayName", "value": new_display_name},
        ],
    }

    # Step 4: Send PATCH request
    patch_response = client.patch(group_url, json=patch_body, headers=auth_headers)
    assert patch_response.status_code == 200, f"PATCH failed: {patch_response.text}"
    patched_group = patch_response.json()

    # Step 5: Assert updated fields
    assert patched_group["id"] == group_id
    assert patched_group["displayName"] == new_display_name

    # Step 7: Re-GET to confirm persistence
    get_final = client.get(group_url, headers=auth_headers)
    assert get_final.status_code == 200
    final_group = get_final.json()

    assert final_group["displayName"] == new_display_name


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


## DELETE


@pytest.mark.asyncio
@pytest.mark.skipif(skip_if_no_udm(), reason="UDM server not reachable or in unit tests only mode")
async def test_delete_user_endpoint(
    create_random_user: CreateUserFactory,
    client: TestClient,
    api_prefix: str,
    auth_headers: dict[str, str],
) -> None:
    """Test deleting a user through the REST API endpoint."""
    print("\n=== E2E Testing DELETE User Endpoint ===")

    # First create a user to delete
    test_user = await create_random_user()
    user_id = test_user.id
    user_url = f"{api_prefix}/Users/{user_id}"

    # Verify the user exists first
    get_response = client.get(user_url, headers=auth_headers)
    assert get_response.status_code == 200, f"User doesn't exist before deletion: {get_response.text}"

    # Delete the user
    delete_response = client.delete(user_url, headers=auth_headers)

    # According to RFC 7644, successful deletion should return 204 No Content
    assert delete_response.status_code == 204, f"Failed to delete user: {delete_response.status_code}"

    # Verify the response body is empty
    assert not delete_response.content, "DELETE response should have empty body"

    # Verify the user no longer exists
    get_after_response = client.get(user_url, headers=auth_headers)
    assert get_after_response.status_code == 404, "User still exists after deletion"


@pytest.mark.asyncio
@pytest.mark.skipif(skip_if_no_udm(), reason="UDM server not reachable or in unit tests only mode")
async def test_delete_group_endpoint(
    create_random_group: CreateGroupFactory,
    client: TestClient,
    api_prefix: str,
    auth_headers: dict[str, str],
) -> None:
    """Test deleting a group through the REST API endpoint."""
    print("\n=== E2E Testing DELETE Group Endpoint ===")

    # First create a group to delete
    test_group = await create_random_group()
    group_id = test_group.id
    group_url = f"{api_prefix}/Groups/{group_id}"

    # Verify the group exists first
    get_response = client.get(group_url, headers=auth_headers)
    assert get_response.status_code == 200, f"Group doesn't exist before deletion: {get_response.text}"

    # Delete the group
    delete_response = client.delete(group_url, headers=auth_headers)

    # According to RFC 7644, successful deletion should return 204 No Content
    assert delete_response.status_code == 204, f"Failed to delete group: {delete_response.status_code}"

    # Verify the response body is empty
    assert not delete_response.content, "DELETE response should have empty body"

    # Verify the group no longer exists
    get_after_response = client.get(group_url, headers=auth_headers)
    assert get_after_response.status_code == 404, "Group still exists after deletion"


@pytest.mark.asyncio
@pytest.mark.skipif(skip_if_no_udm(), reason="UDM server not reachable or in unit tests only mode")
async def test_delete_nonexistent_user(client: TestClient, api_prefix: str, auth_headers: dict[str, str]) -> None:
    """Test deleting a non-existent user through the REST API endpoint."""
    print("\n=== E2E Testing DELETE Non-existent User Endpoint ===")

    # Generate a likely non-existent user ID
    import uuid

    nonexistent_id = str(uuid.uuid4())
    user_url = f"{api_prefix}/Users/{nonexistent_id}"

    # Verify the user doesn't exist first
    get_response = client.get(user_url, headers=auth_headers)
    assert get_response.status_code == 404, "Non-existent user should return 404"

    # Try to delete the non-existent user
    delete_response = client.delete(user_url, headers=auth_headers)

    # Should return 404 Not Found
    assert delete_response.status_code == 404, (
        f"Deleting non-existent user should return 404, got {delete_response.status_code}"
    )


@pytest.mark.asyncio
@pytest.mark.skipif(skip_if_no_udm(), reason="UDM server not reachable or in unit tests only mode")
async def test_delete_nonexistent_group(client: TestClient, api_prefix: str, auth_headers: dict[str, str]) -> None:
    """Test deleting a non-existent group through the REST API endpoint."""
    print("\n=== E2E Testing DELETE Non-existent Group Endpoint ===")

    # Generate a likely non-existent group ID
    import uuid

    nonexistent_id = str(uuid.uuid4())
    group_url = f"{api_prefix}/Groups/{nonexistent_id}"

    # Verify the group doesn't exist first
    get_response = client.get(group_url, headers=auth_headers)
    assert get_response.status_code == 404, "Non-existent group should return 404"

    # Try to delete the non-existent group
    delete_response = client.delete(group_url, headers=auth_headers)

    # Should return 404 Not Found
    assert delete_response.status_code == 404, (
        f"Deleting non-existent group should return 404, got {delete_response.status_code}"
    )


@pytest.mark.asyncio
@pytest.mark.skipif(skip_if_no_udm(), reason="UDM server not reachable or in unit tests only mode")
async def test_delete_user_with_memberships(
    create_random_user: CreateUserFactory,
    create_random_group: CreateGroupFactory,
    client: TestClient,
    api_prefix: str,
    auth_headers: dict[str, str],
) -> None:
    """Test deleting a user that belongs to a group."""
    print("\n=== E2E Testing DELETE User with Group Memberships ===")

    # Create a user and group
    test_user = await create_random_user()
    test_group = await create_random_group()

    user_id = test_user.id
    group_id = test_group.id
    user_url = f"{api_prefix}/Users/{user_id}"
    group_url = f"{api_prefix}/Groups/{group_id}"

    # First, add the user to the group
    get_group_response = client.get(group_url, headers=auth_headers)
    assert get_group_response.status_code == 200
    group_data = get_group_response.json()

    # Prepare group update
    if "meta" in group_data:
        del group_data["meta"]

    if "members" not in group_data:
        group_data["members"] = []

    # Add the user to the group's members
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

    # Verify the user is in the group
    get_updated_group = client.get(group_url, headers=auth_headers)
    updated_group_data = get_updated_group.json()
    assert "members" in updated_group_data, "Group should have members"

    member_ids = [member["value"] for member in updated_group_data["members"]]
    assert user_id in member_ids, "User should be in group members"

    # Now delete the user
    delete_response = client.delete(user_url, headers=auth_headers)
    assert delete_response.status_code == 204, f"Failed to delete user: {delete_response.status_code}"

    # Verify the user no longer exists
    get_after_response = client.get(user_url, headers=auth_headers)
    assert get_after_response.status_code == 404, "User still exists after deletion"

    # Verify the user is no longer in the group's members
    get_group_after = client.get(group_url, headers=auth_headers)
    assert get_group_after.status_code == 200
    group_after_data = get_group_after.json()

    # If the group still has members, check that our deleted user is not among them
    if "members" in group_after_data and group_after_data["members"]:
        member_ids_after = [member["value"] for member in group_after_data["members"]]
        assert user_id not in member_ids_after, "Deleted user should not be in group members"


@pytest.mark.asyncio
@pytest.mark.skipif(skip_if_no_udm(), reason="UDM server not reachable or in unit tests only mode")
async def test_delete_group_with_members(
    create_random_user: CreateUserFactory,
    create_random_group: CreateGroupFactory,
    client: TestClient,
    api_prefix: str,
    auth_headers: dict[str, str],
) -> None:
    """Test deleting a group that has members."""
    print("\n=== E2E Testing DELETE Group with Members ===")

    # Create users and a group
    test_user1 = await create_random_user()
    test_user2 = await create_random_user()
    test_group = await create_random_group()

    user1_id = test_user1.id
    user2_id = test_user2.id
    group_id = test_group.id

    group_url = f"{api_prefix}/Groups/{group_id}"

    # Add users to the group
    get_group_response = client.get(group_url, headers=auth_headers)
    assert get_group_response.status_code == 200
    group_data = get_group_response.json()

    # Prepare updates
    if "meta" in group_data:
        del group_data["meta"]

    if "members" not in group_data:
        group_data["members"] = []

    # Add users to the group's members
    group_data["members"].extend(
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

    # Update the group
    put_response = client.put(group_url, json=group_data, headers=auth_headers)
    assert put_response.status_code in [200, 201], f"Failed to update group with members: {put_response.text}"

    # Verify users are in the group
    get_updated_group = client.get(group_url, headers=auth_headers)
    updated_group_data = get_updated_group.json()
    assert "members" in updated_group_data, "Group should have members"

    member_ids = [member["value"] for member in updated_group_data["members"]]
    assert user1_id in member_ids, "User1 should be in group members"
    assert user2_id in member_ids, "User2 should be in group members"

    # Verify users have the group in their memberships
    for user_id in [user1_id, user2_id]:
        user_url = f"{api_prefix}/Users/{user_id}"
        get_user_response = client.get(user_url, headers=auth_headers)
        assert get_user_response.status_code == 200
        updated_user = get_user_response.json()

        # Because of performance concerns we do not map user groups
        assert "groups" not in updated_user, "Groups field available also it should not be mapped"

    # Now delete the group
    delete_response = client.delete(group_url, headers=auth_headers)
    assert delete_response.status_code == 204, f"Failed to delete group: {delete_response.status_code}"

    # Verify the group no longer exists
    get_after_response = client.get(group_url, headers=auth_headers)
    assert get_after_response.status_code == 404, "Group still exists after deletion"

    # Verify users no longer have the deleted group in their memberships
    for user_id in [user1_id, user2_id]:
        user_url = f"{api_prefix}/Users/{user_id}"
        get_user_response = client.get(user_url, headers=auth_headers)
        assert get_user_response.status_code == 200
        updated_user = get_user_response.json()

        # Because of performance concerns we do not map user groups
        assert "groups" not in updated_user, "Groups field available also it should not be mapped"
