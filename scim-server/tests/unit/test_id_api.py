# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH
from faker import Faker
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
    password="securepassword",
    active=True,
    emails=[
        Email(
            value="john.doe@example.org",
            type="work",
            primary=True,
        )
    ],
)

test_group = Group(
    display_name="Test Group",
)


def _create_test_user(client: TestClient) -> str:
    """Helper method to create a test user and return the ID."""
    response = client.post("/scim/v2/Users", json=test_user.model_dump(by_alias=True, exclude_none=True))
    assert response.status_code == 201
    data = response.json()
    return str(data["id"])


def _create_test_group(client: TestClient) -> str:
    """Helper method to create a test group and return the ID."""
    response = client.post("/scim/v2/Groups", json=test_group.model_dump(by_alias=True, exclude_none=True))
    assert response.status_code == 201
    data = response.json()
    return str(data["id"])


class TestIdAPI:
    """Tests for the global UUID endpoints of the SCIM API."""

    def test_get_user_by_id(self, client: TestClient) -> None:
        # First create a user and group
        user_id = _create_test_user(client)
        _create_test_group(client)

        # Get the user
        response = client.get(f"/scim/v2/{user_id}")
        assert response.status_code == 200
        data = response.json()

        # Verify response data
        assert data["id"] == user_id
        assert data["userName"] == test_user.user_name
        assert data["name"]["givenName"] == test_user.name.given_name
        assert data["name"]["familyName"] == test_user.name.family_name

    def test_get_group_by_id(self, client: TestClient) -> None:
        # First create a user and group
        _create_test_user(client)
        group_id = _create_test_group(client)

        # Get the group
        response = client.get(f"/scim/v2/{group_id}")

        assert response.status_code == 200
        data = response.json()

        # Verify response data
        assert data["id"] == group_id
        assert data["displayName"] == test_group.display_name

    def test_object_not_found(self, client: TestClient) -> None:
        # First create a user and group
        _create_test_user(client)
        _create_test_group(client)

        # Get the user
        fake = Faker()
        response = client.get(f"/scim/v2/{fake.uuid4()}")
        assert response.status_code == 404
        data = response.json()
        assert data["schemas"] == ["urn:ietf:params:scim:api:messages:2.0:Error"]
