# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

from faker import Faker
from fastapi.testclient import TestClient
from scim2_models import Group


test_group = Group(
    display_name="Test Group",
)


def _create_test_group(client: TestClient) -> str:
    """Helper method to create a test group and return the ID."""
    response = client.post("/scim/v2/Groups", json=test_group.model_dump(by_alias=True, exclude_none=True))
    assert response.status_code == 201
    data = response.json()
    return str(data["id"])


class TestGroupAPI:
    """Tests for the Group endpoints of the SCIM API."""

    def test_create_group(self, client: TestClient) -> None:
        """Test creating a group."""
        response = client.post("/scim/v2/Groups", json=test_group.model_dump(by_alias=True, exclude_none=True))

        assert response.status_code == 201
        data = response.json()

        # Verify response data
        assert data["displayName"] == test_group.display_name
        assert "id" in data

    def test_list_groups(self, client: TestClient) -> None:
        """Test listing groups."""
        response = client.get("/scim/v2/Groups")

        assert response.status_code == 200
        data = response.json()

        # Verify response structure
        assert "schemas" in data
        assert "urn:ietf:params:scim:api:messages:2.0:ListResponse" in data["schemas"]
        assert "totalResults" in data
        assert "Resources" in data
        assert isinstance(data["Resources"], list)

    def test_get_group(self, client: TestClient) -> None:
        """Test retrieving a group."""
        # First create a group
        group_id = _create_test_group(client)

        # Get the group
        response = client.get(f"/scim/v2/Groups/{group_id}")

        assert response.status_code == 200
        data = response.json()

        # Verify response data
        assert data["id"] == group_id
        assert data["displayName"] == test_group.display_name

    def test_apply_patch_operation(self, client: TestClient) -> None:
        """Test creating a group."""

        group_id = _create_test_group(client)
        group_url = f"/scim/v2/Groups/{group_id}"

        # Step 2: Fetch the group before patching
        pre_patch_response = client.get(group_url)
        assert pre_patch_response.status_code == 200, f"Failed to fetch group: {pre_patch_response.text}"
        original_group = pre_patch_response.json()
        # Verify response data
        assert original_group["displayName"] == test_group.display_name

        # Step 3: Prepare SCIM-compliant patch payload
        patch_operations = {
            "Operations": [
                {"op": "replace", "path": "displayName", "value": "It's not a cult"},
            ]
        }

        # Step 4: Send PATCH request
        patch_response = client.patch(
            group_url,
            json=patch_operations,
            headers={"Content-Type": "application/json"},
        )

        assert patch_response.status_code == 200, f"PATCH failed: {patch_response.text}"
        data = patch_response.json()

        # Step 5: Verify updated values
        assert data["displayName"] == "It's not a cult"
        assert "id" in data

    def test_get_nonexistent_group(self, client: TestClient) -> None:
        """Test getting a nonexistent group."""
        # First create a group, so a valid group is available
        _create_test_group(client)

        fake = Faker()
        response = client.get(f"/scim/v2/Groups/{fake.uuid4()}")
        assert response.status_code == 404

    def test_patch_nonexistent_group(self, client: TestClient) -> None:
        """PATCHing a non-existent group should return 404 or a handled error."""
        # First create a grouo, so a valid group is available
        _create_test_group(client)

        fake = Faker()
        patch_url = f"/scim/v2/Groups/{fake.uuid4()}"

        patch_operations = {
            "Operations": [
                {"op": "replace", "path": "displayName", "value": "GhostGroup"},
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
        group_id = _create_test_group(client)
        group_url = f"/scim/v2/Groups/{group_id}"

        pre_patch_response = client.get(group_url)
        assert pre_patch_response.status_code == 200, f"Failed to fetch group: {pre_patch_response.text}"
        data = pre_patch_response.json()

        assert data["displayName"] == test_group.display_name

        patch_operations = {
            "Operations": [
                {"op": "replace", "path": "bad_field", "value": "oops"},
            ]
        }
        patch_response = client.patch(
            group_url,
            json=patch_operations,
            headers={"Content-Type": "application/json"},
        )

        assert patch_response.status_code == 400
        assert " validation error " in patch_response.text

    def test_patch_with_invalid_payload_broken(self, client: TestClient) -> None:
        """PATCH with malformed data should be rejected with 400."""
        group_id = _create_test_group(client)
        group_url = f"/scim/v2/Groups/{group_id}"

        pre_patch_response = client.get(group_url)
        assert pre_patch_response.status_code == 200, f"Failed to fetch group: {pre_patch_response.text}"
        original_group = pre_patch_response.json()
        assert original_group["displayName"] != "Cult group"

        invalid_patch = {"bad_field": "oops"}

        patch_response = client.patch(
            group_url,
            json=invalid_patch,
            headers={"Content-Type": "application/json"},
        )

        assert patch_response.status_code == 400
        assert "Operations" in patch_response.text or "Invalid" in patch_response.text

    def test_patch_remove_attribute(self, client: TestClient) -> None:
        """PATCH to remove a group attribute should succeed and result in deletion."""
        group_id = _create_test_group(client)
        group_url = f"/scim/v2/Groups/{group_id}"

        # Confirm field exists before deletion
        group_before = client.get(group_url).json()
        assert "displayName" in group_before

        # Remove the 'displayName' field
        patch_operations = {
            "Operations": [
                {"op": "remove", "path": "displayName"},
            ]
        }

        patch_response = client.patch(
            group_url,
            json=patch_operations,
            headers={"Content-Type": "application/json"},
        )

        assert patch_response.status_code == 400  # should retry to remove it but since its not allowed it should fail
