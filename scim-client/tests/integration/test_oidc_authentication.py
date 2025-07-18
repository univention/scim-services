# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

import os
from collections.abc import Generator

import pytest
from keycloak import KeycloakAdmin, KeycloakOpenID, KeycloakPostError

from univention.scim.client.authentication import Authenticator, AuthenticatorSettings, GetTokenError


AUDIENCE = "nubus-scim"
REALM = "master"


@pytest.fixture(scope="session")
def keycloak_base_url() -> str:
    return os.environ["KEYCLOAK_BASE_URL"]


@pytest.fixture(scope="session")
def authenticator_settings(keycloak_base_url: str) -> AuthenticatorSettings:
    return AuthenticatorSettings(
        scim_client_id="scim-client-test-client",
        scim_client_secret="supersecret",
        scim_oidc_token_url=f"{keycloak_base_url}/realms/master/protocol/openid-connect/token",
    )


@pytest.fixture(scope="session")
def keycloak_admin(keycloak_base_url: str) -> KeycloakAdmin:
    keycloak_admin = KeycloakAdmin(
        server_url=keycloak_base_url,
        username="admin",
        password="univention",
        realm_name=REALM,
        verify=True,
    )
    return keycloak_admin


@pytest.fixture(scope="session")
def audience_client_scope(keycloak_admin: KeycloakAdmin) -> Generator[str, None, None]:
    scope_id = "e0f7c5f0-1234-5678-90ab-cdef12345678"

    scope_name = f"{AUDIENCE}-test-scope"
    scope_payload = {"name": scope_name, "protocol": "openid-connect", "id": scope_id}
    try:
        scope_id = keycloak_admin.create_client_scope(scope_payload)
    except KeycloakPostError as error:
        if error.response_code != 409:
            raise

    mapper_payload = {
        "name": "audience-mapper",
        "protocol": "openid-connect",
        "protocolMapper": "oidc-audience-mapper",
        "config": {
            "included.client.audience": AUDIENCE,
            "access.token.claim": "true",
        },
    }
    keycloak_admin.add_mapper_to_client_scope(
        client_scope_id=scope_id,
        payload=mapper_payload,
    )

    yield scope_id
    keycloak_admin.delete_client_scope(scope_id)


@pytest.fixture(scope="session", autouse=True)
def scim_http_client(
    keycloak_admin: KeycloakAdmin, authenticator_settings: AuthenticatorSettings, audience_client_scope: str
) -> Generator[None, None, None]:
    keycloak_client_id = "e0f7c5f0-1234-5678-90ab-cdef12345678"
    client_representation = {
        "id": keycloak_client_id,
        "clientId": authenticator_settings.scim_client_id,
        "secret": authenticator_settings.scim_client_secret,
        "protocol": "openid-connect",
        "publicClient": False,
        "serviceAccountsEnabled": True,
        "standardFlowEnabled": False,
        "directAccessGrantsEnabled": False,
    }
    try:
        actual_client_id = keycloak_admin.create_client(client_representation)
        assert actual_client_id == keycloak_client_id
    except KeycloakPostError as error:
        if error.response_code != 409:
            raise

    if keycloak_client_id:
        keycloak_admin.add_client_default_client_scope(
            client_id=keycloak_client_id, client_scope_id=audience_client_scope, payload={}
        )

    yield
    keycloak_admin.delete_client(keycloak_client_id)


def test_authentication(authenticator_settings: AuthenticatorSettings) -> None:
    authenticator = Authenticator(authenticator_settings)

    token = authenticator.get_token()

    assert token


@pytest.mark.parametrize(
    "customization",
    [
        {"scim_client_id": "invalid-client-id"},
        {"scim_client_secret": "invalid-secret"},
        {"scim_oidc_token_url": "https://wrong-url.xyz"},
    ],
)
def test_failed_authentication(customization: dict[str, str], authenticator_settings: AuthenticatorSettings) -> None:
    customized_settings = authenticator_settings.model_copy(update=customization)
    print(customized_settings)

    authenticator = Authenticator(customized_settings)

    with pytest.raises(GetTokenError):
        authenticator.get_token()


def test_token_has_audience(authenticator_settings: AuthenticatorSettings, keycloak_base_url: str) -> None:
    authenticator = Authenticator(authenticator_settings)

    token = authenticator.get_token()
    assert token

    keycloak_openid = KeycloakOpenID(
        server_url=keycloak_base_url,
        client_id=authenticator_settings.scim_client_id,
        client_secret_key=authenticator_settings.scim_client_secret,
        realm_name=REALM,
        verify=True,
    )

    decoded_token = keycloak_openid.decode_token(token)
    assert "nubus-scim" in decoded_token["aud"]
