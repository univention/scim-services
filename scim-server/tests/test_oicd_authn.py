# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

from collections.abc import Generator
from typing import Any

import pytest
from fastapi.testclient import TestClient
from jwcrypto.jwk import JWK
from jwcrypto.jwt import JWT
from pytest_httpserver.httpserver import HTTPServer

from univention.scim.server.authn.authn_impl import OpenIDConnectAuthentication
from univention.scim.server.authn.oidc_configuration_impl import OpenIDConnectConfigurationImpl
from univention.scim.server.config import AuthenticatorConfig
from univention.scim.server.container import ApplicationContainer


@pytest.fixture
def oicd_auth(setup_mocks: None, httpserver: HTTPServer) -> Generator[JWK, None, None]:
    jwks_uri = "/oauth2/v3/certs"
    oidc_configuration_url = "/.well-known/openid-configuration"

    key = JWK.generate(kty="RSA", size=2048, alg="RS256", use="sig", kid="good")
    oidc_configuration = {
        "jwks_uri": httpserver.url_for(jwks_uri),
        "id_token_signing_alg_values_supported": [key.alg],
        "authorization_endpoint": httpserver.url_for("/authorize"),
        "token_endpoint": httpserver.url_for("/token"),
    }

    httpserver.expect_request(oidc_configuration_url).respond_with_json(oidc_configuration)
    httpserver.expect_request(jwks_uri).respond_with_json({"keys": [key.export(private_key=False, as_dict=True)]})

    oidc_configuration_obj = OpenIDConnectConfigurationImpl(
        AuthenticatorConfig(idp_openid_configuration_url=httpserver.url_for(oidc_configuration_url))
    )

    with (
        ApplicationContainer.authenticator.override(OpenIDConnectAuthentication(oidc_configuration_obj, "scim-api")),
        ApplicationContainer.oidc_configuration.override(oidc_configuration_obj),
    ):
        yield key


@pytest.mark.xfail(strict=True, raises=ValueError)
def test_oicd_invalid_configuration(request: Any, oicd_auth: JWK, httpserver: HTTPServer) -> None:
    oidc_configuration = {
        "authorization_endpoint": httpserver.url_for("/authorize"),
        "token_endpoint": httpserver.url_for("/token"),
    }

    httpserver.clear_all_handlers()
    httpserver.expect_request("/.well-known/openid-configuration").respond_with_json(oidc_configuration)
    # setting up the client should throw an exception because oidc_configuration is invalid
    request.getfixturevalue("client")


@pytest.mark.xfail(strict=True, raises=ValueError)
def test_oicd_no_route(request: Any, oicd_auth: JWK, httpserver: HTTPServer) -> None:
    httpserver.clear_all_handlers()
    # setting up the client should throw an exception because oidc configuration URL is not accessible
    request.getfixturevalue("client")


def test_oicd_auth(oicd_auth: JWK, client: TestClient) -> None:
    claims = {"uid": "Test User", "azp": "scim-api"}
    header = {"alg": oicd_auth.alg}
    jwt = JWT(header=header, claims=claims)
    jwt.make_signed_token(oicd_auth)

    response = client.get("/scim/v2/Users", headers={"Authorization": f"Bearer {jwt.serialize()}"})
    assert response.status_code == 200


def test_oicd_auth_wrong_client_id(oicd_auth: JWK, client: TestClient) -> None:
    claims = {"uid": "Test User", "azp": "not-scim-api"}
    header = {"alg": oicd_auth.alg}
    jwt = JWT(header=header, claims=claims)
    jwt.make_signed_token(oicd_auth)

    response = client.get("/scim/v2/Users", headers={"Authorization": f"Bearer {jwt.serialize()}"})
    assert response.status_code == 403


def test_oicd_auth_wrong_signature(oicd_auth: JWK, client: TestClient) -> None:
    claims = {"uid": "Test User", "azp": "scim-api"}
    header = {"alg": oicd_auth.alg}
    jwt = JWT(header=header, claims=claims)

    test_key = JWK.generate(kty="RSA", size=2048, alg="RS256", use="sig", kid="good")
    jwt.make_signed_token(test_key)

    response = client.get("/scim/v2/Users", headers={"Authorization": f"Bearer {jwt.serialize()}"})
    assert response.status_code == 403


def test_oicd_auth_missing_kid(oicd_auth: JWK, client: TestClient) -> None:
    claims = {"uid": "Test User", "azp": "scim-api"}
    header = {"alg": oicd_auth.alg}
    jwt = JWT(header=header, claims=claims)

    test_key = JWK.generate(kty="RSA", size=2048, alg="RS256", use="sig", kid="fail")
    jwt.make_signed_token(test_key)

    response = client.get("/scim/v2/Users", headers={"Authorization": f"Bearer {jwt.serialize()}"})
    assert response.status_code == 403


def test_oicd_auth_mandatory_claim_uid_missing(oicd_auth: JWK, client: TestClient) -> None:
    claims = {"azp": "scim-api"}
    header = {"alg": oicd_auth.alg}
    jwt = JWT(header=header, claims=claims)
    jwt.make_signed_token(oicd_auth)

    response = client.get("/scim/v2/Users", headers={"Authorization": f"Bearer {jwt.serialize()}"})
    assert response.status_code == 403


def test_oicd_auth_mandatory_claim_azp_missing(oicd_auth: JWK, client: TestClient) -> None:
    claims = {"uid": "Test User"}
    header = {"alg": oicd_auth.alg}
    jwt = JWT(header=header, claims=claims)
    jwt.make_signed_token(oicd_auth)

    response = client.get("/scim/v2/Users", headers={"Authorization": f"Bearer {jwt.serialize()}"})
    assert response.status_code == 403
