import pytest
from fastapi.testclient import TestClient

from tests.conftest import skip_if_no_udm, api_prefix, auth_headers, CreateGroupFactory, CreateUserFactory




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
