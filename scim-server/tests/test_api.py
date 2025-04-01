# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

from typing import Any

import pytest
from fastapi.testclient import TestClient
from scim2_models import Email, Group, Name, User


# Test data
test_user = User(
    user_name="jdoe",
    name=Name(
        given_name="John",
        family_name="Doe",
        formatted="John Doe",
    ),
    active=True,
    emails=[
        Email(
            value="john.doe@example.com",
            type="work",
            primary=True,
        )
    ],
)

test_group = Group(
    display_name="Test Group",
)


class TestUserAPI:
    """Tests for the User endpoints of the SCIM API."""

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

    def test_create_user(self, client: TestClient) -> Any:
        """Test creating a user."""
        response = client.post("/scim/v2/Users", json=test_user.model_dump(by_alias=True, exclude_none=True))
        assert response.status_code == 201
        data = response.json()

        # Verify response data
        assert data["userName"] == test_user.user_name
        assert data["name"]["givenName"] == test_user.name.given_name
        assert data["name"]["familyName"] == test_user.name.family_name
        assert "id" in data

        # Save the ID for other tests
        user_id = data["id"]
        return user_id

    def test_get_user(self, client: TestClient) -> None:
        """Test retrieving a user."""
        # First create a user
        user_id = self.test_create_user(client)

        # Get the user
        response = client.get(f"/scim/v2/Users/{user_id}")
        assert response.status_code == 200
        data = response.json()

        # Verify response data
        assert data["id"] == user_id
        assert data["userName"] == test_user.user_name
        assert data["name"]["givenName"] == test_user.name.given_name
        assert data["name"]["familyName"] == test_user.name.family_name

    def test_update_user(self, client: TestClient) -> None:
        """Test updating a user."""
        # First create a user
        user_id = self.test_create_user(client)

        # Update the user
        updated_user = test_user.model_copy()
        updated_user.name.given_name = "Jane"

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

    def test_delete_user(self, client: TestClient) -> None:
        """Test deleting a user."""
        # First create a user
        user_id = self.test_create_user(client)

        # Delete the user
        response = client.delete(f"/scim/v2/Users/{user_id}")
        assert response.status_code == 204

        # Verify the user is deleted
        response = client.get(f"/scim/v2/Users/{user_id}")
        assert response.status_code == 404

    def test_get_nonexistent_user(self, client: TestClient) -> None:
        """Test getting a nonexistent user."""
        response = client.get("/scim/v2/Users/nonexistent")
        assert response.status_code == 404

    def test_update_nonexistent_user(self, client: TestClient) -> None:
        """Test updating a nonexistent user."""
        response = client.put("/scim/v2/Users/nonexistent", json=test_user.model_dump(by_alias=True, exclude_none=True))
        assert response.status_code == 404

    def test_delete_nonexistent_user(self, client: TestClient) -> None:
        """Test deleting a nonexistent user."""
        response = client.delete("/scim/v2/Users/nonexistent")
        assert response.status_code == 404

    def test_filter_users(self, client: TestClient) -> None:
        """Test filtering users."""
        # First create a user
        self.test_create_user(client)

        # Filter users by userName
        response = client.get(f"/scim/v2/Users?filter=userName eq {test_user.user_name}")
        assert response.status_code == 200
        data = response.json()

        # Verify filtered results
        assert data["totalResults"] >= 1
        assert any(u["userName"] == test_user.user_name for u in data["Resources"])


class TestGroupAPI:
    """Tests for the Group endpoints of the SCIM API."""

    def test_list_groups(self, client: TestClient) -> None:
        """Test listing groups."""
        response = client.get("/scim/v2/Groups")
        # For now, this might return 501 Not Implemented
        if response.status_code == 501:
            pytest.skip("Group listing not implemented yet")

        assert response.status_code == 200
        data = response.json()

        # Verify response structure
        assert "schemas" in data
        assert "urn:ietf:params:scim:api:messages:2.0:ListResponse" in data["schemas"]
        assert "totalResults" in data
        assert "Resources" in data
        assert isinstance(data["Resources"], list)

    def test_create_group(self, client: TestClient) -> Any:
        """Test creating a group."""
        response = client.post("/scim/v2/Groups", json=test_group.model_dump(by_alias=True, exclude_none=True))

        # For now, this might return 501 Not Implemented
        if response.status_code == 501:
            pytest.skip("Group creation not implemented yet")

        assert response.status_code == 201
        data = response.json()

        # Verify response data
        assert data["displayName"] == test_group.display_name
        assert "id" in data

        # Save the ID for other tests
        group_id = data["id"]
        return group_id

    def test_get_group(self, client: TestClient) -> None:
        """Test retrieving a group."""
        try:
            # First create a group
            group_id = self.test_create_group(client)
        except pytest.skip.Exception:
            pytest.skip("Group creation not implemented yet")

        # Get the group
        response = client.get(f"/scim/v2/Groups/{group_id}")

        # For now, this might return 501 Not Implemented
        if response.status_code == 501:
            pytest.skip("Group retrieval not implemented yet")

        assert response.status_code == 200
        data = response.json()

        # Verify response data
        assert data["id"] == group_id
        assert data["displayName"] == test_group.display_name


class TestServiceProviderConfig:
    """Tests for the ServiceProviderConfig endpoint."""

    def test_get_service_provider_config(self, client: TestClient) -> None:
        """Test retrieving the service provider configuration."""
        response = client.get("/scim/v2/ServiceProviderConfig")
        assert response.status_code == 200
        data = response.json()

        # Verify required fields
        assert "schemas" in data
        assert "urn:ietf:params:scim:schemas:core:2.0:ServiceProviderConfig" in data["schemas"]
        assert "patch" in data
        assert "bulk" in data
        assert "filter" in data
        assert "changePassword" in data
        assert "sort" in data
        assert "etag" in data
        assert "authenticationSchemes" in data
