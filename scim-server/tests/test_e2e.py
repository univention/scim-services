# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

import os
from collections.abc import Generator
from typing import cast

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from scim2_models import Group, User

from univention.scim.server.config import ApplicationSettings
from univention.scim.server.container import ApplicationContainer
from univention.scim.server.main import app

from .conftest import (
    skip_if_no_udm,
)


@pytest.fixture
def test_app() -> FastAPI:
    """Create a test instance of the FastAPI application."""
    return cast(FastAPI, app)


@pytest.fixture
def test_client(test_app: FastAPI) -> Generator[TestClient, None, None]:
    """Create a test client for the FastAPI application that properly handles async lifespan."""
    with TestClient(test_app) as client:
        yield client


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

    # This fixture ONLY bypasses authentication, not the repositories
    application_settings.auth_enabled = False

    with (
        ApplicationContainer.authenticator.override(AllowAllBearerAuthentication()),
        ApplicationContainer.oidc_configuration.override(OpenIDConnectConfigurationMock()),
        ApplicationContainer.settings.override(application_settings),
    ):
        yield


@pytest.mark.skipif(skip_if_no_udm(), reason="UDM server not reachable or in unit tests only mode")
@pytest.mark.usefixtures("maildomain", "disable_auththentication")
def test_get_user_endpoint(
    user_fixture: User, test_client: TestClient, api_prefix: str, auth_headers: dict[str, str]
) -> None:
    """Test retrieving a user through the REST API endpoint."""
    print("\n=== E2E Testing GET User Endpoint ===")

    user_id = user_fixture.id
    user_url = f"{api_prefix}/Users/{user_id}"

    response = test_client.get(user_url, headers=auth_headers)

    assert response.status_code == 200, f"Failed to get user: {response.text}"
    user_data = response.json()

    # Verify essential user properties
    assert user_data["id"] == user_id
    assert user_data["userName"] == user_fixture.user_name
    assert user_data["displayName"] == user_fixture.display_name

    # Verify nested properties
    assert user_data["name"]["givenName"] == user_fixture.name.given_name
    assert user_data["name"]["familyName"] == user_fixture.name.family_name

    # Verify email addresses
    primary_email = next((email for email in user_data["emails"] if email.get("primary", False)), None)
    assert primary_email is not None, "No primary email found"
    assert primary_email["value"] in [email.value for email in user_fixture.emails]


@pytest.mark.skipif(skip_if_no_udm(), reason="UDM server not reachable or in unit tests only mode")
@pytest.mark.usefixtures("disable_auththentication")
def test_get_group_endpoint(
    group_fixture: Group, test_client: TestClient, api_prefix: str, auth_headers: dict[str, str]
) -> None:
    """Test retrieving a group through the REST API endpoint."""
    print("\n=== E2E Testing GET Group Endpoint ===")

    group_id = group_fixture.id
    group_url = f"{api_prefix}/Groups/{group_id}"

    response = test_client.get(group_url, headers=auth_headers)

    assert response.status_code == 200, f"Failed to get group: {response.text}"
    group_data = response.json()

    # Verify essential group properties
    assert group_data["id"] == group_id
    assert group_data["displayName"] == group_fixture.display_name
