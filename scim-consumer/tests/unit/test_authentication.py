# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

from unittest.mock import MagicMock

import pytest
from jwcrypto.jwt import JWTExpired
from keycloak import KeycloakAuthenticationError, KeycloakOpenID

from univention.scim.consumer.authentication import Authenticator, AuthenticatorSettings, GetTokenError


@pytest.fixture
def authenticator_settings() -> AuthenticatorSettings:
    return AuthenticatorSettings(
        scim_client_id="client-id",
        scim_client_secret="client-secret",
        scim_idp_base_url="http://keycloak-url",
        scim_idp_realm="idp-realm",
        scim_idp_audience="idp-audience",
    )


@pytest.fixture
def authenticator(authenticator_settings):
    mock_keycloak: KeycloakOpenID = MagicMock(KeycloakOpenID)

    def mock_keycloak_adapter(*args, **kwargs):
        return mock_keycloak

    authenticator = Authenticator(authenticator_settings, keycloak_adapter=mock_keycloak_adapter)
    return authenticator


# src/univention/scim/consumer/authentication.py
# 40     22    45%   29-30, 38-45, 48-58, 61-63


def test_authenticator_new_token(authenticator: Authenticator):
    authenticator.keycloak.token.return_value = {"access_token": "new-dummy-token"}

    token = authenticator.get_token()

    assert token == "new-dummy-token"


def test_authenticator_existing_token(authenticator: Authenticator):
    authenticator.access_token = "dummy-token"

    token = authenticator.get_token()

    assert token == "dummy-token"


def test_authenticator_expired_token(authenticator: Authenticator):
    authenticator.access_token = "expired-dummy-token"
    authenticator.keycloak.decode_token.side_effect = JWTExpired("dummy-expired-event")
    authenticator.keycloak.token.return_value = {"access_token": "new-dummy-token"}

    token = authenticator.get_token()
    assert token == "new-dummy-token"
    authenticator.keycloak.decode_token.assert_called_once_with("expired-dummy-token")
    authenticator.keycloak.token.assert_called_once_with(grant_type="client_credentials")


def test_authenticator_error_response(authenticator: Authenticator):
    authenticator.keycloak.token.return_value = {"access_token": None, "error": "some-keycloak-response"}

    with pytest.raises(GetTokenError) as excinfo:
        authenticator.get_token()
    assert "some-keycloak-response" in str(excinfo.value)


def test_authenticator_keycloak_exception(authenticator: Authenticator):
    authenticator.keycloak.token.side_effect = KeycloakAuthenticationError("keycloak-error-string")

    with pytest.raises(GetTokenError) as error:
        authenticator.get_token()

    assert isinstance(error.value.__cause__, KeycloakAuthenticationError)
    assert str(error.value.__cause__) == "keycloak-error-string"
