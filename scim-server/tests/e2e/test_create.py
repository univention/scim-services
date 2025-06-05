# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

import pytest
from fastapi.testclient import TestClient
from scim2_models import Group, User

from tests.conftest import skip_if_no_udm


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
