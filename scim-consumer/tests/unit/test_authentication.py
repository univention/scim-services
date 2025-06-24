# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

import base64
import json
import time
from unittest.mock import MagicMock

import httpx
import pytest

from univention.scim.consumer.authentication import Authenticator, AuthenticatorSettings, GetTokenError


def _make_jwt(exp: float) -> str:
    """Helper to craft a dummy JWT with only an exp claim."""
    payload = json.dumps({"exp": exp}).encode()
    b64 = base64.urlsafe_b64encode(payload).rstrip(b"=").decode()
    return f"header.{b64}.signature"


@pytest.fixture
def authenticator_settings() -> AuthenticatorSettings:
    return AuthenticatorSettings(
        scim_client_id="client-id",
        scim_client_secret="client-secret",
        scim_oidc_token_url="http://keycloak-url",
    )


@pytest.fixture
def mock_response() -> httpx.Response:
    mock_response = MagicMock(httpx.Response)
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {"access_token": "new-dummy-token"}
    return mock_response


@pytest.fixture
def authenticator(authenticator_settings, mock_response) -> Authenticator:
    mock_client: httpx.Client = MagicMock(httpx.Client)
    mock_client.post.return_value = mock_response

    authenticator = Authenticator(authenticator_settings, http_client=mock_client)
    return authenticator


def test_authenticator_new_token(authenticator: Authenticator):
    token = authenticator.get_token()

    assert token == "new-dummy-token"
    authenticator._client.post.assert_called_once()


def test_authenticator_existing_token(authenticator: Authenticator):
    expected_token = _make_jwt(time.time() + 3600)
    authenticator._access_token = expected_token

    actual_token = authenticator.get_token()

    assert actual_token == expected_token


def test_authenticator_expired_token(authenticator: Authenticator):
    authenticator._access_token = _make_jwt(time.time() - 1)

    token = authenticator.get_token()
    assert token == "new-dummy-token"
    authenticator._client.post.assert_called_once()


def test_authenticator_error_response(authenticator: Authenticator, mock_response):
    error = httpx.HTTPStatusError("500 internal-test-error", request=None, response=None)
    mock_response.raise_for_status.side_effect = error

    with pytest.raises(GetTokenError) as excinfo:
        authenticator.get_token()
    assert excinfo.value.__cause__ == error


def test_authenticator_connection_error(authenticator: Authenticator):
    expected_error = httpx.RequestError("test-connection-error", request=None)
    authenticator._client.post.side_effect = expected_error

    with pytest.raises(GetTokenError) as error:
        authenticator.get_token()

    assert error.value.__cause__ == expected_error
