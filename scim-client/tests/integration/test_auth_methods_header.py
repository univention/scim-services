# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

import httpx

from univention.scim.client.authentication import BearerAuth, BearerAuthSettings

from ..data.scim_helper import capture_authorization_header


def test_none_auth_sends_no_authorization_header(scim_server_base_url: str) -> None:
    authorization_header = capture_authorization_header(scim_server_base_url, None)

    assert authorization_header is None


def test_basic_auth_header_reaches_scim_server(scim_server_base_url: str) -> None:
    auth = httpx.BasicAuth("integration-test-user", "integration-test-password")

    authorization_header = capture_authorization_header(scim_server_base_url, auth)

    assert authorization_header is not None
    assert authorization_header.startswith("Basic ")


def test_bearer_auth_header_reaches_scim_server(scim_server_base_url: str) -> None:
    settings = BearerAuthSettings(scim_bearer_token="integration-test-static-token")
    auth = BearerAuth(settings)

    authorization_header = capture_authorization_header(scim_server_base_url, auth)

    assert authorization_header == "Bearer integration-test-static-token"
