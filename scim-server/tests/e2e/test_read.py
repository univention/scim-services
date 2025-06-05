import pytest
from scim2_models import  GroupMember
from fastapi.testclient import TestClient

from tests.conftest import skip_if_no_udm, api_prefix, auth_headers, CreateGroupFactory, CreateUserFactory

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
