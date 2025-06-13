# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

import pytest
from fastapi.testclient import TestClient

from helpers.udm_client import MockUdm


@pytest.fixture
def force_mock() -> bool:
    return True


def test_user_external_id_filter(udm_client: MockUdm, client: TestClient) -> None:
    """Test filtering users by externalId"""
    # Create a test user
    test_user = udm_client.add_user()

    response = client.get(f'/scim/v2/Users?filter=externalId eq "{test_user.properties["testExternalId"]}"')

    assert response.status_code == 200
    data = response.json()
    assert data["totalResults"] == 1
    assert len(data["Resources"]) == 1
    assert data["Resources"][0]["id"] == test_user.properties["univentionObjectIdentifier"]
    assert data["Resources"][0]["externalId"] == test_user.properties["testExternalId"]


def test_group_external_id_filter(udm_client: MockUdm, client: TestClient) -> None:
    """Test filtering groups by externalId"""
    # Create a test group
    test_group = udm_client.add_group()

    response = client.get(f'/scim/v2/Groups?filter=externalId eq "{test_group.properties["testExternalId"]}"')

    assert response.status_code == 200
    data = response.json()
    assert data["totalResults"] == 1
    assert len(data["Resources"]) == 1
    assert data["Resources"][0]["id"] == test_group.properties["univentionObjectIdentifier"]
    assert data["Resources"][0]["externalId"] == test_group.properties["testExternalId"]


def test_user_external_id_filter_no_match(udm_client: MockUdm, client: TestClient) -> None:
    """Test filtering users by externalId with no matching results."""
    # Create a test user
    udm_client.add_user()

    # Filter by non-existent externalId
    response = client.get('/scim/v2/Users?filter=externalId eq "non-existent-id"')

    assert response.status_code == 200
    data = response.json()
    assert data["totalResults"] == 0
    assert len(data["Resources"]) == 0


def test_group_external_id_filter_no_match(udm_client: MockUdm, client: TestClient) -> None:
    """Test filtering groups by externalId with no matching results."""
    # Create a test group
    udm_client.add_group()

    # Filter by non-existent externalId
    response = client.get('/scim/v2/Groups?filter=externalId eq "non-existent-id"')

    assert response.status_code == 200
    data = response.json()
    assert data["totalResults"] == 0
    assert len(data["Resources"]) == 0


def test_user_external_id_filter_multiple_users(udm_client: MockUdm, client: TestClient) -> None:
    """Test filtering users by externalId when multiple users exist."""
    # Create multiple test users
    udm_client.add_user()
    user2 = udm_client.add_user()
    udm_client.add_user()

    # Filter by specific user's externalId
    response = client.get(f'/scim/v2/Users?filter=externalId eq "{user2.properties["testExternalId"]}"')

    assert response.status_code == 200
    data = response.json()
    assert data["totalResults"] == 1
    assert len(data["Resources"]) == 1
    assert data["Resources"][0]["id"] == user2.properties["univentionObjectIdentifier"]
    assert data["Resources"][0]["externalId"] == user2.properties["testExternalId"]


def test_group_external_id_filter_multiple_groups(udm_client: MockUdm, client: TestClient) -> None:
    """Test filtering groups by externalId when multiple groups exist."""
    # Create multiple test groups
    udm_client.add_group()
    group2 = udm_client.add_group()
    udm_client.add_group()

    # Filter by specific group's externalId
    response = client.get(f'/scim/v2/Groups?filter=externalId eq "{group2.properties["testExternalId"]}"')

    assert response.status_code == 200
    data = response.json()
    assert data["totalResults"] == 1
    assert len(data["Resources"]) == 1
    assert data["Resources"][0]["id"] == group2.properties["univentionObjectIdentifier"]
    assert data["Resources"][0]["externalId"] == group2.properties["testExternalId"]


def test_external_id_filter_with_pagination(udm_client: MockUdm, client: TestClient) -> None:
    """Test externalId filtering works correctly with pagination parameters."""
    # Create a test user
    test_user = udm_client.add_user()

    # Filter with pagination parameters
    response = client.get(
        f'/scim/v2/Users?filter=externalId eq "{test_user.properties["testExternalId"]}"&startIndex=1&count=10'
    )

    assert response.status_code == 200
    data = response.json()
    assert data["totalResults"] == 1
    assert len(data["Resources"]) == 1
    assert data["Resources"][0]["id"] == test_user.properties["univentionObjectIdentifier"]
    assert data["Resources"][0]["externalId"] == test_user.properties["testExternalId"]
    assert data["startIndex"] == 1
    assert data["itemsPerPage"] == 1


def test_external_id_filter_case_sensitivity(udm_client: MockUdm, client: TestClient) -> None:
    """Test that externalId filtering is case sensitive."""
    # Create a test user
    test_user = udm_client.add_user()
    original_id = test_user.properties["testExternalId"]

    # Filter with uppercase UUID (should not match)
    response = client.get(f'/scim/v2/Users?filter=externalId eq "{original_id.upper()}"')

    assert response.status_code == 200
    data = response.json()
    assert data["totalResults"] == 0
    assert len(data["Resources"]) == 0

    # Filter with correct case (should match)
    response = client.get(f'/scim/v2/Users?filter=externalId eq "{original_id}"')

    assert response.status_code == 200
    data = response.json()
    assert data["totalResults"] == 1
    assert len(data["Resources"]) == 1
    assert data["Resources"][0]["id"] == test_user.properties["univentionObjectIdentifier"]
    assert data["Resources"][0]["externalId"] == test_user.properties["testExternalId"]
