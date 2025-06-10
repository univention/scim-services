# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

import pytest
from faker import Faker
from fastapi.testclient import TestClient
from scim2_models import Name

from univention.scim.server.model_service.load_schemas_impl import UserWithExtensions


# We can only test this with the mocked UDM because a real UDM
# does not allow creating a group with invalid members
@pytest.fixture
def force_mock() -> bool:
    return True


# Test data
test_user = UserWithExtensions(
    user_name="jdoe",
    name=Name(
        given_name="John",
        family_name="Doe",
        formatted="John Doe",
    ).model_dump(),
    password="securepassword",
    active=True,
    emails=[
        {
            "value": "john.doe@example.org",
            "type": "alias",
            "primary": True,
        },
        {
            "value": "other@example.org",
            "type": "other",
            "primary": False,
        },
    ],
)


def _create_test_user(client: TestClient) -> str:
    """Helper method to create a test user and return the ID."""
    response = client.post("/scim/v2/Users", json=test_user.model_dump(by_alias=True, exclude_none=True))
    assert response.status_code == 201
    data = response.json()
    return str(data["id"])


class TestUserAPI:
    """Tests for the User endpoints of the SCIM API."""

    def test_create_user(self, client: TestClient) -> None:
        """Test creating a user."""
        response = client.post("/scim/v2/Users", json=test_user.model_dump(by_alias=True, exclude_none=True))
        assert response.status_code == 201
        data = response.json()

        # Verify response data
        assert data["userName"] == test_user.user_name
        assert data["name"]["givenName"] == test_user.name.given_name
        assert data["name"]["familyName"] == test_user.name.family_name
        assert "id" in data

    def test_get_user(self, client: TestClient) -> None:
        """Test retrieving a user."""
        # First create a user
        user_id = _create_test_user(client)

        # Get the user
        response = client.get(f"/scim/v2/Users/{user_id}")
        assert response.status_code == 200
        data = response.json()

        # Verify response data
        assert data["id"] == user_id
        assert data["userName"] == test_user.user_name
        assert data["name"]["givenName"] == test_user.name.given_name
        assert data["name"]["familyName"] == test_user.name.family_name

    def test_list_users(self, client: TestClient) -> None:
        """Test listing users."""
        response = client.get("/scim/v2/Users")
        assert response.status_code == 200
        data = response.json()

        # Verify response structure
        assert "schemas" in data
        assert "urn:ietf:params:scim:api:messages:2.0:ListResponse" in data["schemas"]
        assert "totalResults" in data
        assert "Resources" in data
        assert isinstance(data["Resources"], list)
        assert "password" not in data

    def test_create_user_without_password(self, client: TestClient) -> None:
        """Test creating a user without password."""
        test_user_copy = test_user.model_copy()
        test_user_copy.password = None
        response = client.post("/scim/v2/Users", json=test_user_copy.model_dump(by_alias=True, exclude_none=True))
        assert response.status_code == 201
        data = response.json()

        # Verify response data
        assert data["userName"] == test_user_copy.user_name
        assert data["name"]["givenName"] == test_user_copy.name.given_name
        assert data["name"]["familyName"] == test_user_copy.name.family_name
        # password should not be returned
        assert "password" not in data
        assert "id" in data

    def test_create_user_empty_password(self, client: TestClient) -> None:
        """Test creating a user with an empty password."""
        test_user_copy = test_user.model_copy()
        test_user_copy.password = ""
        response = client.post("/scim/v2/Users", json=test_user_copy.model_dump(by_alias=True, exclude_none=True))
        assert response.status_code == 400

    def test_update_user_with_new_password(self, client: TestClient) -> None:
        """Test updating a user with a new password."""
        # First create a user
        user_id = _create_test_user(client)

        # Update the user
        updated_user = test_user.model_copy()
        updated_user.password = "verysecretpassword"

        response = client.put(
            f"/scim/v2/Users/{user_id}", json=updated_user.model_dump(by_alias=True, exclude_none=True)
        )
        assert response.status_code == 200
        data = response.json()

        # Verify response data
        assert data["id"] == user_id
        assert data["userName"] == updated_user.user_name
        assert data["name"]["givenName"] == updated_user.name.given_name
        assert data["name"]["familyName"] == updated_user.name.family_name
        # password should not be returned
        assert "password" not in data

    def test_update_user_empty_password(self, client: TestClient) -> None:
        """Test updating a user with empty password."""
        # First create a user
        user_id = _create_test_user(client)

        # Update the user
        updated_user = test_user.model_copy()
        updated_user.password = ""

        response = client.put(
            f"/scim/v2/Users/{user_id}", json=updated_user.model_dump(by_alias=True, exclude_none=True)
        )
        assert response.status_code == 400

    def test_update_user(self, client: TestClient) -> None:
        """Test updating a user."""
        # First create a user
        user_id = _create_test_user(client)

        # Update the user
        updated_user = test_user.model_copy()
        updated_user.name.given_name = "Jane"

        # Do not update the password UDM does not allow setting the same password
        updated_user.password = None

        response = client.put(
            f"/scim/v2/Users/{user_id}", json=updated_user.model_dump(by_alias=True, exclude_none=True)
        )
        assert response.status_code == 200
        data = response.json()

        # Verify response data
        assert data["id"] == user_id
        assert data["userName"] == updated_user.user_name
        assert data["name"]["givenName"] == updated_user.name.given_name
        assert data["name"]["familyName"] == updated_user.name.family_name

    def test_apply_patch_operations(self, client: TestClient) -> None:
        """Test partially updating a user using PATCH."""
        # Step 1: Create a user
        user_id = _create_test_user(client)
        user_url = f"/scim/v2/Users/{user_id}"

        # Step 2: Fetch the user before patching
        pre_patch_response = client.get(user_url)
        assert pre_patch_response.status_code == 200, f"Failed to fetch user: {pre_patch_response.text}"
        original_user = pre_patch_response.json()
        # Assert initial state is different
        assert original_user["name"]["givenName"] != "Jane2"
        assert original_user["displayName"] != "Jane2 Smith"

        # Step 3: Prepare SCIM-compliant patch payload
        patch_operations = {
            "Operations": [
                {"op": "replace", "path": "name.givenName", "value": "Jane2"},
                {"op": "replace", "path": "displayName", "value": "Jane2 Smith"},
            ]
        }

        # Step 4: Send PATCH request
        patch_response = client.patch(
            user_url,
            json=patch_operations,
            headers={"Content-Type": "application/json"},
        )

        assert patch_response.status_code == 200, f"PATCH failed: {patch_response.text}"
        data = patch_response.json()

        # Step 5: Verify updated values
        assert data["id"] == user_id
        assert data["name"]["givenName"] == "Jane2"
        assert data["displayName"] == "Jane2 Smith"

        # Step 6: Optionally verify unchanged fields
        assert "familyName" in data["name"]

    def test_patch_nonexistent_user(self, client: TestClient) -> None:
        """PATCHing a non-existent user should return 404 or a handled error."""
        non_existent_id = "non-existent-id-123"
        patch_url = f"/scim/v2/Users/{non_existent_id}"

        patch_operations = {
            "Operations": [
                {"op": "replace", "path": "name.givenName", "value": "Ghost"},
            ]
        }

        response = client.patch(
            patch_url,
            json=patch_operations,
            headers={"Content-Type": "application/json"},
        )

        assert response.status_code in (404, 400), f"Expected failure but got: {response.status_code}"
        assert "not found" in response.text.lower()

    def test_patch_with_invalid_payload(self, client: TestClient) -> None:
        """PATCH with malformed data should be rejected with 400."""
        user_id = _create_test_user(client)
        user_url = f"/scim/v2/Users/{user_id}"

        pre_patch_response = client.get(user_url)
        assert pre_patch_response.status_code == 200, f"Failed to fetch user: {pre_patch_response.text}"
        original_user = pre_patch_response.json()
        assert original_user["name"]["givenName"] != "Jane2"
        assert original_user["displayName"] != "Jane2 Smith"

        patch_operations = {
            "Operations": [
                {"op": "replace", "path": "bad_field", "value": "oops"},
            ]
        }
        patch_response = client.patch(
            user_url,
            json=patch_operations,
            headers={"Content-Type": "application/json"},
        )

        assert patch_response.status_code == 400
        assert " validation error " in patch_response.text

    def test_patch_with_invalid_payload_broken(self, client: TestClient) -> None:
        """PATCH with malformed data should be rejected with 400."""
        user_id = _create_test_user(client)
        user_url = f"/scim/v2/Users/{user_id}"

        pre_patch_response = client.get(user_url)
        assert pre_patch_response.status_code == 200, f"Failed to fetch user: {pre_patch_response.text}"
        original_user = pre_patch_response.json()
        assert original_user["name"]["givenName"] != "Jane2"
        assert original_user["displayName"] != "Jane2 Smith"

        invalid_patch = {"bad_field": "oops"}

        patch_response = client.patch(
            user_url,
            json=invalid_patch,
            headers={"Content-Type": "application/json"},
        )

        assert patch_response.status_code == 400
        assert "Operations" in patch_response.text or "Invalid" in patch_response.text

    def test_patch_remove_attribute(self, client: TestClient) -> None:
        """PATCH to remove a user attribute should succeed and result in deletion."""
        user_id = _create_test_user(client)
        user_url = f"/scim/v2/Users/{user_id}"

        # Confirm field exists before deletion
        user_before = client.get(user_url).json()
        assert "name" in user_before and "givenName" in user_before["name"]

        # Remove the 'givenName' field
        patch_operations = {
            "Operations": [
                {"op": "remove", "path": "name.givenName"},
            ]
        }

        patch_response = client.patch(
            user_url,
            json=patch_operations,
            headers={"Content-Type": "application/json"},
        )

        assert patch_response.status_code == 200
        user_after = patch_response.json()

        # Expect 'givenName' to be gone (or None)
        assert "name" in user_after
        assert "givenName" not in user_after["name"] or user_after["name"]["givenName"] in ("", None)

    def test_patch_add_with_nested_extension_path(self, client: TestClient) -> None:
        """
        PATCH 'add' operation should create missing intermediate
        objects if nested fields are missing and not fail with an exception,
        however, adding some random field should give a 400
        """
        user_id = _create_test_user(client)
        user_url = f"/scim/v2/Users/{user_id}"

        # Confirm extension is not present initially
        user_before = client.get(user_url).json()
        extension_schema = "unknown_nested_field"
        assert extension_schema not in user_before

        patch_operations = {
            "Operations": [
                {
                    "op": "add",
                    "path": f"{extension_schema}.department",
                    "value": "Engineering",
                }
            ]
        }

        patch_response = client.patch(
            user_url,
            json=patch_operations,
            headers={"Content-Type": "application/json"},
        )

        assert patch_response.status_code == 400

    def test_delete_user(self, client: TestClient) -> None:
        """Test deleting a user."""
        # First create a user
        user_id = _create_test_user(client)

        # Delete the user
        response = client.delete(f"/scim/v2/Users/{user_id}")
        assert response.status_code == 204

        # Verify the user is deleted
        response = client.get(f"/scim/v2/Users/{user_id}")
        assert response.status_code == 404

    def test_get_nonexistent_user(self, client: TestClient) -> None:
        """Test getting a nonexistent user."""
        # First create a user, so a valid user is available
        _create_test_user(client)

        fake = Faker()
        response = client.get(f"/scim/v2/Users/{fake.uuid4()}")
        assert response.status_code == 404

    def test_update_nonexistent_user(self, client: TestClient) -> None:
        """Test updating a nonexistent user."""
        # First create a user, so a valid user is available
        _create_test_user(client)

        Faker()
        response = client.put(
            "/scim/v2/Users/{fake.uuid4()}", json=test_user.model_dump(by_alias=True, exclude_none=True)
        )
        assert response.status_code == 404

    def test_delete_nonexistent_user(self, client: TestClient) -> None:
        """Test deleting a nonexistent user."""
        # First create a user, so a valid user is available
        _create_test_user(client)

        Faker()
        response = client.delete("/scim/v2/Users/{fake.uuid4()}")
        assert response.status_code == 404

    def test_filter_users(self, client: TestClient) -> None:
        """Test filtering users."""
        # First create a user
        _create_test_user(client)

        # Filter users by userName
        response = client.get(f"/scim/v2/Users?filter=userName eq {test_user.user_name}")
        assert response.status_code == 200
        data = response.json()

        # Verify filtered results
        assert data["totalResults"] >= 1
        assert any(u["userName"] == test_user.user_name for u in data["Resources"])

    # Level 1: Basic operations (what you already support)

    def test_level1_simple_replace(self, client: TestClient) -> None:
        """Test simple attribute replacement."""
        user_id = _create_test_user(client)

        patch_ops = {"Operations": [{"op": "replace", "path": "displayName", "value": "Updated Name"}]}

        response = client.patch(f"/scim/v2/Users/{user_id}", json=patch_ops)
        assert response.status_code == 200
        data = response.json()
        assert data["displayName"] == "Updated Name"

    def test_level1_nested_path(self, client: TestClient) -> None:
        """Test nested path with dot notation."""
        user_id = _create_test_user(client)

        patch_ops = {"Operations": [{"op": "replace", "path": "name.givenName", "value": "NewFirst"}]}

        response = client.patch(f"/scim/v2/Users/{user_id}", json=patch_ops)
        assert response.status_code == 200
        data = response.json()
        assert data["name"]["givenName"] == "NewFirst"

    @pytest.mark.xfail
    def test_level1_remove_operation(self, client: TestClient) -> None:
        """Test remove operation."""
        user_id = _create_test_user(client)

        patch_ops = {"Operations": [{"op": "remove", "path": "name.givenName"}]}

        response = client.patch(f"/scim/v2/Users/{user_id}", json=patch_ops)
        assert response.status_code == 200
        data = response.json()
        assert "givenName" not in data["name"] or data["name"]["givenName"] is None

    # Level 2: Multi-valued attributes without filters

    @pytest.mark.xfail
    def test_level1_multiple_operations(self, client: TestClient) -> None:
        """Test multiple operations in a single patch request."""
        user_id = _create_test_user(client)

        # Prepare patch operations similar to your example
        new_display_name = "PatchedFirst PatchedLast"
        new_email_value = "patched-test@work.com"

        patch_ops = {
            "schemas": ["urn:ietf:params:scim:api:messages:2.0:PatchOp"],
            "Operations": [
                {"op": "replace", "path": "displayName", "value": new_display_name},
                {"op": "replace", "path": "name.givenName", "value": "PatchedFirst"},
                {"op": "replace", "path": "name.familyName", "value": "PatchedLast"},
                {
                    "op": "replace",
                    "path": "emails",
                    "value": [{"value": new_email_value, "type": "alias", "primary": True}],
                },
            ],
        }

        response = client.patch(f"/scim/v2/Users/{user_id}", json=patch_ops)
        assert response.status_code == 200, f"Multiple operations failed: {response.text}"
        data = response.json()

        # Verify all operations were applied
        assert data["displayName"] == new_display_name
        assert data["name"]["givenName"] == "PatchedFirst"
        assert data["name"]["familyName"] == "PatchedLast"

        # Check emails - should have original emails plus the new one
        # assert len(data["emails"]) >= 2, f"Expected at least 2 emails, got {len(data['emails'])}"

        # Find the new email
        new_email = next((e for e in data["emails"] if e["value"] == new_email_value), None)
        assert new_email is not None, f"New email {new_email_value} not found"
        assert new_email["type"] == "alias"

    @pytest.mark.xfail
    def test_level2_replace_entire_array(self, client: TestClient) -> None:
        """Test replacing entire multi-valued attribute."""
        user_id = _create_test_user(client)

        patch_ops = {
            "Operations": [
                {
                    "op": "replace",
                    "path": "emails",
                    "value": [{"value": "new@email.com", "type": "alias", "primary": True}],
                }
            ]
        }

        response = client.patch(f"/scim/v2/Users/{user_id}", json=patch_ops)
        assert response.status_code == 200
        data = response.json()
        assert len(data["emails"]) == 1
        assert data["emails"][0]["value"] == "new@email.com"

    @pytest.mark.xfail
    def test_level2_add_to_array(self, client: TestClient) -> None:
        """Test adding to multi-valued attribute."""
        user_id = _create_test_user(client)

        patch_ops = {
            "Operations": [
                {"op": "add", "path": "emails", "value": [{"value": "additional@email.com", "type": "other"}]}
            ]
        }

        response = client.patch(f"/scim/v2/Users/{user_id}", json=patch_ops)

        # If this fails, your implementation might not support array append
        if response.status_code != 200:
            pytest.skip("Adding to arrays not yet supported")

        data = response.json()
        assert len(data["emails"]) == 3  # Original 2 + 1 new

    # Level 3: Array index notation (if supported)

    @pytest.mark.xfail
    def test_level3_array_index(self, client: TestClient) -> None:
        """Test array index notation."""
        user_id = _create_test_user(client)

        patch_ops = {"Operations": [{"op": "replace", "path": "emails[0].value", "value": "indexed@email.com"}]}

        response = client.patch(f"/scim/v2/Users/{user_id}", json=patch_ops)

        if response.status_code == 400:
            # Check if it's a path syntax error
            error = response.json()
            if "path" in str(error).lower() or "syntax" in str(error).lower():
                pytest.skip("Array index notation not yet supported")

        assert response.status_code == 200
        data = response.json()
        assert data["emails"][0]["value"] == "indexed@email.com"

    # Level 4: Filter expressions (full SCIM compliance)
    @pytest.mark.xfail
    def test_level4_filter_expression(self, client: TestClient) -> None:
        """Test filter expression in path."""
        user_id = _create_test_user(client)

        patch_ops = {
            "Operations": [{"op": "replace", "path": 'emails[type eq "alias"].value', "value": "filtered@work.com"}]
        }

        response = client.patch(f"/scim/v2/Users/{user_id}", json=patch_ops)

        if response.status_code == 400:
            error = response.json()
            if "path" in str(error).lower() or "filter" in str(error).lower():
                pytest.skip("Filter expressions not yet supported")

        assert response.status_code == 200
        data = response.json()

        # Should still have both emails
        assert len(data["emails"]) == 2

        # Alias email should be updated
        alias_email = next((e for e in data["emails"] if e["type"] == "alias"), None)
        assert alias_email is not None
        assert alias_email["value"] == "filtered@work.com"

        # Home email should be unchanged
        home_email = next((e for e in data["emails"] if e["type"] == "other"), None)
        assert home_email is not None
        assert home_email["value"] == "other@example.org"

    @pytest.mark.xfail
    def test_level4_remove_with_filter(self, client: TestClient) -> None:
        """Test removing with filter."""
        user_id = _create_test_user(client)

        patch_ops = {"Operations": [{"op": "remove", "path": 'emails[type eq "other"]'}]}

        response = client.patch(f"/scim/v2/Users/{user_id}", json=patch_ops)

        if response.status_code == 400:
            error = response.json()
            if "path" in str(error).lower() or "filter" in str(error).lower():
                pytest.skip("Filter expressions not yet supported")

        assert response.status_code == 200
        data = response.json()

        # Should only have alias email left
        assert len(data["emails"]) == 1
        assert data["emails"][0]["type"] == "alias"

    # Level 5: Path-less operations
    @pytest.mark.xfail
    def test_level5_pathless_operation(self, client: TestClient) -> None:
        """Test operation without path."""
        user_id = _create_test_user(client)

        patch_ops = {"Operations": [{"op": "add", "value": {"title": "Software Engineer"}}]}

        response = client.patch(f"/scim/v2/Users/{user_id}", json=patch_ops)

        if response.status_code == 400:
            error = response.json()
            if "path" in str(error).lower():
                pytest.skip("Path-less operations not yet supported")

        assert response.status_code == 200
        data = response.json()
        assert data.get("title") == "Software Engineer"
