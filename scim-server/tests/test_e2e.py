# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

import os
from collections.abc import Callable, Generator

import pytest
from fastapi.testclient import TestClient
from scim2_models import Group, User

from univention.scim.server.config import ApplicationSettings
from univention.scim.server.container import ApplicationContainer

from .conftest import (
    skip_if_no_udm,
)


@pytest.fixture
def api_prefix() -> str:
    """Get the API prefix for the SCIM server."""
    return os.environ.get("API_PREFIX", "/scim/v2")


@pytest.fixture
def auth_headers() -> dict[str, str]:
    """Get authentication headers for API requests."""
    # In a real E2E test, we would use actual authentication
    # For now, return empty dict if auth is disabled or mock headers if enabled
    auth_enabled = os.environ.get("AUTH_ENABLED", "false").lower() == "true"
    if auth_enabled:
        return {"Authorization": "Bearer test-token"}
    return {}


@pytest.fixture(autouse=True)
def e2e_auth_bypass(application_settings: ApplicationSettings) -> Generator[None, None, None]:
    """Bypass authentication for E2E tests without replacing repositories"""
    from helpers.allow_all_authn import AllowAllBearerAuthentication, OpenIDConnectConfigurationMock

    with (
        ApplicationContainer.authenticator.override(AllowAllBearerAuthentication()),
        ApplicationContainer.oidc_configuration.override(OpenIDConnectConfigurationMock()),
    ):
        yield


@pytest.mark.asyncio
@pytest.mark.skipif(skip_if_no_udm(), reason="UDM server not reachable or in unit tests only mode")
@pytest.mark.usefixtures("maildomain")
async def test_list_user_endpoint(
    create_random_user: Callable[[], User], client: TestClient, api_prefix: str, auth_headers: dict[str, str]
) -> None:
    """Test retrieving a list of user through the REST API endpoint."""
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
@pytest.mark.usefixtures("maildomain")
async def test_get_user_endpoint(
    create_random_user: Callable[[], User], client: TestClient, api_prefix: str, auth_headers: dict[str, str]
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
def test_get_group_endpoint(
    group_fixture: Group, client: TestClient, api_prefix: str, auth_headers: dict[str, str]
) -> None:
    """Test retrieving a group through the REST API endpoint."""
    print("\n=== E2E Testing GET Group Endpoint ===")

    group_id = group_fixture.id
    group_url = f"{api_prefix}/Groups/{group_id}"

    response = client.get(group_url, headers=auth_headers)

    assert response.status_code == 200, f"Failed to get group: {response.text}"
    group_data = response.json()

    # Verify essential group properties
    assert group_data["id"] == group_id
    assert group_data["displayName"] == group_fixture.display_name
