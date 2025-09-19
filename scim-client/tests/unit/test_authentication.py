# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

import base64
import json
import time
from unittest.mock import MagicMock

import httpx
import pytest

from univention.scim.client.authentication import Authenticator, AuthenticatorSettings, GetTokenError


def _make_jwt(exp: float) -> str:
    """Helper to craft a dummy JWT with only an exp claim."""
    payload = json.dumps({"exp": exp}).encode()
    b64 = base64.urlsafe_b64encode(payload).rstrip(b"=").decode()
    return f"header.{b64}.signature"


def _make_jwt_with_invalid_json() -> str:
    """Helper to craft a JWT with invalid JSON in the payload."""
    invalid_json = b"invalid-json-payload"
    b64 = base64.urlsafe_b64encode(invalid_json).rstrip(b"=").decode()
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
def authenticator(authenticator_settings: AuthenticatorSettings, mock_response: httpx.Response) -> Authenticator:
    mock_client: httpx.Client = MagicMock(httpx.Client)
    mock_client.post.return_value = mock_response  # type: ignore

    authenticator = Authenticator(authenticator_settings, http_client=mock_client)
    return authenticator


def test_authenticator_new_token(authenticator: Authenticator) -> None:
    token = authenticator.get_token()

    assert token == "new-dummy-token"
    authenticator._client.post.assert_called_once()


def test_authenticator_existing_token(authenticator: Authenticator) -> None:
    expected_token = _make_jwt(time.time() + 3600)
    authenticator._access_token = expected_token

    actual_token = authenticator.get_token()

    assert actual_token == expected_token


def test_authenticator_expired_token(authenticator: Authenticator) -> None:
    authenticator._access_token = _make_jwt(time.time() - 1)

    token = authenticator.get_token()
    assert token == "new-dummy-token"
    authenticator._client.post.assert_called_once()


def test_authenticator_error_response(authenticator: Authenticator, mock_response: httpx.Response) -> None:
    error = httpx.HTTPStatusError("500 internal-test-error", request=None, response=None)  # type: ignore
    mock_response.raise_for_status.side_effect = error  # type: ignore

    with pytest.raises(GetTokenError) as excinfo:
        authenticator.get_token()
    assert excinfo.value.__cause__ == error


def test_authenticator_connection_error(authenticator: Authenticator) -> None:
    expected_error = httpx.RequestError("test-connection-error", request=None)
    authenticator._client.post.side_effect = expected_error

    with pytest.raises(GetTokenError) as error:
        authenticator.get_token()

    assert error.value.__cause__ == expected_error


@pytest.mark.parametrize(
    "malformed_token",
    [
        pytest.param("not-a-jwt-token", id="no-dots"),
        pytest.param("header.invalid-base64.signature", id="invalid-base64"),
        pytest.param("header..signature", id="empty-payload"),
        pytest.param("header.signature", id="missing-payload-section"),
        pytest.param(_make_jwt_with_invalid_json(), id="invalid-json-payload"),
    ],
)
def test_authenticator_malformed_jwt_tokens(authenticator: Authenticator, malformed_token: str) -> None:
    """Test that malformed JWT tokens are handled gracefully and result in token refresh."""
    authenticator._access_token = malformed_token

    # Should get a new token when the existing one is malformed
    token = authenticator.get_token()
    assert token == "new-dummy-token"


def test_authenticator_jwt_without_exp_claim(authenticator: Authenticator) -> None:
    """Test that JWT without 'exp' claim is handled optimistically."""
    import base64
    import json

    # Create a JWT payload without the 'exp' claim
    payload = json.dumps({"sub": "user123", "iat": 1234567890}).encode()
    b64 = base64.urlsafe_b64encode(payload).rstrip(b"=").decode()
    jwt_without_exp = f"header.{b64}.signature"

    authenticator._access_token = jwt_without_exp

    # Should pass through the token optimistically when no 'exp' claim present
    token = authenticator.get_token()
    assert token == jwt_without_exp
    authenticator._client.post.assert_not_called()


def test_authenticator_plain_json_token(authenticator: Authenticator) -> None:
    """Test that plain JSON tokens from Keycloak are handled correctly."""
    # Create a plain JSON token (not encoded JWT format) with valid exp claim
    future_exp = time.time() + 3600
    plain_json_token = json.dumps({"exp": future_exp, "sub": "user123", "aud": "scim-api"})

    authenticator._access_token = plain_json_token

    # Should use existing token when it's valid plain JSON
    token = authenticator.get_token()
    assert token == plain_json_token
    authenticator._client.post.assert_not_called()


def test_authenticator_plain_json_expired_token(authenticator: Authenticator) -> None:
    """Test that expired plain JSON tokens trigger token refresh."""
    # Create a plain JSON token with expired exp claim
    expired_exp = time.time() - 1
    plain_json_token = json.dumps({"exp": expired_exp, "sub": "user123", "aud": "scim-api"})

    authenticator._access_token = plain_json_token

    # Should get a new token when plain JSON token is expired
    token = authenticator.get_token()
    assert token == "new-dummy-token"
    authenticator._client.post.assert_called_once()


def test_authenticator_plain_json_without_exp_claim(authenticator: Authenticator) -> None:
    """Test that plain JSON tokens without 'exp' claim are handled optimistically."""
    # Create a plain JSON token without the 'exp' claim
    plain_json_token = json.dumps({"sub": "user123", "aud": "scim-api"})

    authenticator._access_token = plain_json_token

    # Should pass through the token optimistically when no 'exp' claim present
    token = authenticator.get_token()
    assert token == plain_json_token
    authenticator._client.post.assert_not_called()


def test_authenticator_string_exp_claims(authenticator: Authenticator) -> None:
    """Test that string 'exp' claims are handled correctly (fixes TypeError issue)."""
    import time

    current_time = time.time()

    # Test valid string exp claim (future)
    valid_string_exp_token = json.dumps(
        {
            "exp": str(int(current_time + 3600)),  # String instead of number
            "iat": int(current_time),
            "client_id": "scim-client",
        }
    )

    authenticator._access_token = valid_string_exp_token
    token = authenticator.get_token()
    assert token == valid_string_exp_token  # Should reuse valid token
    authenticator._client.post.assert_not_called()

    # Test expired string exp claim (past)
    expired_string_exp_token = json.dumps(
        {
            "exp": str(int(current_time - 300)),  # Expired string exp
            "iat": int(current_time - 360),
            "client_id": "scim-client",
        }
    )

    authenticator._access_token = expired_string_exp_token
    token = authenticator.get_token()
    assert token == "new-dummy-token"  # Should fetch new token
    authenticator._client.post.assert_called_once()

    # Test invalid exp format
    authenticator._client.post.reset_mock()
    invalid_exp_token = json.dumps({"exp": "invalid-date-format", "client_id": "scim-client"})

    authenticator._access_token = invalid_exp_token
    token = authenticator.get_token()
    assert token == "new-dummy-token"  # Should fetch new token due to invalid exp
    authenticator._client.post.assert_called_once()
