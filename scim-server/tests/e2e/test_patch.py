import pytest
from fastapi.testclient import TestClient

from tests.conftest import skip_if_no_udm, api_prefix, auth_headers, CreateGroupFactory, CreateUserFactory


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
            {"op": "add", "path": "emails", "value": [{"value": new_email_value, "type": "work"}]},
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

    # # Step 6: Check updated emails
    email_values = [e["value"] for e in patched_user["emails"]]
    assert new_email_value in email_values

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
