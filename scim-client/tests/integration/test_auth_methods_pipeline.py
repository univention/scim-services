# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

import multiprocessing
from collections.abc import Generator
from typing import Any

import pytest
from keycloak import KeycloakAdmin, KeycloakPostError
from univention.admin.rest.client import UDM

from univention.scim.client.main import run as scim_client_run
from univention.scim.client.scim_http_client import ScimClient

from ..data.scim_helper import (
    create_provisioning_subscription,
    delete_provisioning_subscription,
    wait_for_resource_deleted,
    wait_for_resource_exists,
)
from ..data.udm_helper import create_udm_user, delete_udm_user


OIDC_CLIENT_ID = "scim-client-pipeline-test-client"
OIDC_CLIENT_SECRET = "supersecret"
OIDC_REALM = "master"


@pytest.fixture(params=["none", "basic", "bearer", "oidc"])
def auth_method(request: pytest.FixtureRequest) -> str:
    return request.param


@pytest.fixture
def keycloak_admin(keycloak_base_url: str) -> KeycloakAdmin:
    return KeycloakAdmin(
        server_url=keycloak_base_url,
        username="admin",
        password="univention",
        realm_name=OIDC_REALM,
        verify=True,
    )


@pytest.fixture
def oidc_client_registration(auth_method: str, keycloak_admin: KeycloakAdmin) -> Generator[None, None, None]:
    """
    Registers a dedicated Keycloak client for the scim-client subprocess to
    authenticate with when auth_method == "oidc". No-op for all other auth
    methods so this fixture is safe to always depend on.
    """
    if auth_method != "oidc":
        yield
        return

    client_representation = {
        "clientId": OIDC_CLIENT_ID,
        "secret": OIDC_CLIENT_SECRET,
        "protocol": "openid-connect",
        "publicClient": False,
        "serviceAccountsEnabled": True,
        "standardFlowEnabled": False,
        "directAccessGrantsEnabled": False,
    }
    try:
        client_id = keycloak_admin.create_client(client_representation)
    except KeycloakPostError as error:
        if error.response_code != 409:
            raise
        client_id = keycloak_admin.get_client_id(OIDC_CLIENT_ID)

    yield

    keycloak_admin.delete_client(client_id)


@pytest.fixture
def scim_client_with_auth_method(
    auth_method: str,
    oidc_client_registration: None,
    keycloak_base_url: str,
    monkeypatch: pytest.MonkeyPatch,
) -> Generator[None, None, None]:
    """
    Runs a real scim-client subprocess (the same entry point used in
    production) configured with the given SCIM_AUTH_METHOD, pushing to the
    live scim-dev-server. Uses its own subscription name so it does not
    conflict with the session-scoped `background_scim_client` used by
    test_main.py.
    """
    monkeypatch.setenv("PROVISIONING_API_USERNAME", f"scim-client-{auth_method}-pipeline-test")
    monkeypatch.setenv("SCIM_AUTH_METHOD", auth_method)
    if auth_method == "basic":
        monkeypatch.setenv("SCIM_BASIC_AUTH_USERNAME", "integration-test-user")
        monkeypatch.setenv("SCIM_BASIC_AUTH_PASSWORD", "integration-test-password")
    elif auth_method == "bearer":
        monkeypatch.setenv("SCIM_BEARER_TOKEN", "integration-test-static-token")
    elif auth_method == "oidc":
        monkeypatch.setenv(
            "SCIM_OIDC_TOKEN_URL", f"{keycloak_base_url}/realms/{OIDC_REALM}/protocol/openid-connect/token"
        )
        monkeypatch.setenv("SCIM_CLIENT_ID", OIDC_CLIENT_ID)
        monkeypatch.setenv("SCIM_CLIENT_SECRET", OIDC_CLIENT_SECRET)

    create_provisioning_subscription()

    proc = multiprocessing.Process(target=scim_client_run)
    proc.start()

    yield

    proc.terminate()
    delete_provisioning_subscription()


def test_user_create_and_delete_with_auth_method(
    scim_client_with_auth_method: None,
    udm_client: UDM,
    scim_http_client: ScimClient,
    user_data: dict[str, Any],
    auth_method: str,
) -> None:
    """
    Proves the full UDM change -> provisioning message -> scim-client ->
    scim-dev-server pipeline works when scim-client is configured with the
    given SCIM_AUTH_METHOD, not just that the auth header can be constructed
    in isolation (see test_auth_methods_header.py / test_oidc_authentication.py
    for those checks).
    """
    create_udm_user(udm_client=udm_client, user_data=user_data)

    user = wait_for_resource_exists(scim_http_client, user_data["univentionObjectIdentifier"])
    assert user, f"User was not synced to SCIM with auth_method={auth_method}"
    assert user.user_name == user_data.get("username")

    delete_udm_user(udm_client=udm_client, user_data=user_data)
    assert wait_for_resource_deleted(scim_http_client, user_data["univentionObjectIdentifier"])
