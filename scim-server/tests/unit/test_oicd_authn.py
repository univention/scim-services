# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

import time
from collections.abc import Callable, Generator
from contextlib import _GeneratorContextManager, contextmanager
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


register_oidc_configuration_url = True


@pytest.fixture
def jwk() -> JWK:
    return JWK.generate(kty="RSA", size=2048, alg="RS256", use="sig", kid="good")


# Override after_setup tets fixture to inject our override
@pytest.fixture
def after_setup(jwk: JWK, httpserver: HTTPServer) -> Callable[[], _GeneratorContextManager[Any, None, None]]:
    @contextmanager
    def override_authenticator() -> Generator[None, None, None]:
        jwks_uri = "/oauth2/v3/certs"
        oidc_configuration_url = "/.well-known/openid-configuration"

        oidc_configuration = {
            "jwks_uri": httpserver.url_for(jwks_uri),
            "id_token_signing_alg_values_supported": [jwk.alg],
            "authorization_endpoint": httpserver.url_for("/authorize"),
            "token_endpoint": httpserver.url_for("/token"),
        }

        global register_oidc_configuration_url
        if register_oidc_configuration_url:
            httpserver.expect_request(oidc_configuration_url).respond_with_json(oidc_configuration)
        else:
            # Reset value for next tests
            register_oidc_configuration_url = True

        httpserver.expect_request(jwks_uri).respond_with_json({"keys": [jwk.export(private_key=False, as_dict=True)]})

        oidc_configuration_obj = OpenIDConnectConfigurationImpl(
            AuthenticatorConfig(idp_openid_configuration_url=httpserver.url_for(oidc_configuration_url))
        )

        with (
            ApplicationContainer.authenticator.override(
                OpenIDConnectAuthentication(oidc_configuration_obj, "scim-api")
            ),
            ApplicationContainer.oidc_configuration.override(oidc_configuration_obj),
        ):
            yield

    return override_authenticator


@pytest.mark.xfail(strict=True, raises=ValueError)
def test_oicd_invalid_configuration(
    request: Any, after_setup: Callable[[], _GeneratorContextManager[Any, None, None]], jwk: JWK, httpserver: HTTPServer
) -> None:
    oidc_configuration = {
        "authorization_endpoint": httpserver.url_for("/authorize"),
        "token_endpoint": httpserver.url_for("/token"),
    }

    httpserver.expect_request("/.well-known/openid-configuration").respond_with_json(oidc_configuration)

    global register_oidc_configuration_url
    register_oidc_configuration_url = False

    # setting up the client should throw an exception because oidc_configuration is invalid
    request.getfixturevalue("client")


@pytest.mark.xfail(strict=True, raises=ValueError)
def test_oicd_no_route(
    request: Any, after_setup: Callable[[], _GeneratorContextManager[Any, None, None]], jwk: JWK, httpserver: HTTPServer
) -> None:
    global register_oidc_configuration_url
    register_oidc_configuration_url = False
    # setting up the client should throw an exception because oidc configuration URL is not accessible
    request.getfixturevalue("client")


def test_oicd_auth(
    after_setup: Callable[[], _GeneratorContextManager[Any, None, None]], jwk: JWK, client: TestClient
) -> None:
    claims = {"uid": "Test User", "azp": "scim-api", "exp": int(time.time()) + 120}
    header = {"alg": jwk.alg}
    jwt = JWT(header=header, claims=claims)
    jwt.make_signed_token(jwk)

    response = client.get("/scim/v2/Users", headers={"Authorization": f"Bearer {jwt.serialize()}"})
    assert response.status_code == 200


def test_oicd_auth_token_expired(
    after_setup: Callable[[], _GeneratorContextManager[Any, None, None]], jwk: JWK, client: TestClient
) -> None:
    claims = {"uid": "Test User", "azp": "scim-api", "exp": int(time.time()) - 120}
    header = {"alg": jwk.alg}
    jwt = JWT(header=header, claims=claims)
    jwt.make_signed_token(jwk)

    response = client.get("/scim/v2/Users", headers={"Authorization": f"Bearer {jwt.serialize()}"})
    assert response.status_code == 403


def test_oicd_auth_wrong_client_id(
    after_setup: Callable[[], _GeneratorContextManager[Any, None, None]], jwk: JWK, client: TestClient
) -> None:
    claims = {"uid": "Test User", "azp": "not-scim-api", "exp": int(time.time()) + 120}
    header = {"alg": jwk.alg}
    jwt = JWT(header=header, claims=claims)
    jwt.make_signed_token(jwk)

    response = client.get("/scim/v2/Users", headers={"Authorization": f"Bearer {jwt.serialize()}"})
    assert response.status_code == 403


def test_oicd_auth_wrong_signature(
    after_setup: Callable[[], _GeneratorContextManager[Any, None, None]], jwk: JWK, client: TestClient
) -> None:
    claims = {"uid": "Test User", "azp": "scim-api", "exp": int(time.time()) + 120}
    header = {"alg": jwk.alg}
    jwt = JWT(header=header, claims=claims)

    test_key = JWK.generate(kty="RSA", size=2048, alg="RS256", use="sig", kid="good")
    jwt.make_signed_token(test_key)

    response = client.get("/scim/v2/Users", headers={"Authorization": f"Bearer {jwt.serialize()}"})
    assert response.status_code == 403


def test_oicd_auth_missing_kid(
    after_setup: Callable[[], _GeneratorContextManager[Any, None, None]], jwk: JWK, client: TestClient
) -> None:
    claims = {"uid": "Test User", "azp": "scim-api", "exp": int(time.time()) + 120}
    header = {"alg": jwk.alg}
    jwt = JWT(header=header, claims=claims)

    test_key = JWK.generate(kty="RSA", size=2048, alg="RS256", use="sig", kid="fail")
    jwt.make_signed_token(test_key)

    response = client.get("/scim/v2/Users", headers={"Authorization": f"Bearer {jwt.serialize()}"})
    assert response.status_code == 403


def test_oicd_auth_mandatory_claim_uid_missing(
    after_setup: Callable[[], _GeneratorContextManager[Any, None, None]], jwk: JWK, client: TestClient
) -> None:
    claims = {"azp": "scim-api", "exp": int(time.time()) + 120}
    header = {"alg": jwk.alg}
    jwt = JWT(header=header, claims=claims)
    jwt.make_signed_token(jwk)

    response = client.get("/scim/v2/Users", headers={"Authorization": f"Bearer {jwt.serialize()}"})
    assert response.status_code == 403


def test_oicd_auth_mandatory_claim_azp_missing(
    after_setup: Callable[[], _GeneratorContextManager[Any, None, None]], jwk: JWK, client: TestClient
) -> None:
    claims = {"uid": "Test User", "exp": int(time.time()) + 120}
    header = {"alg": jwk.alg}
    jwt = JWT(header=header, claims=claims)
    jwt.make_signed_token(jwk)

    response = client.get("/scim/v2/Users", headers={"Authorization": f"Bearer {jwt.serialize()}"})
    assert response.status_code == 403


def test_oicd_auth_mandatory_claim_exp_missing(
    after_setup: Callable[[], _GeneratorContextManager[Any, None, None]], jwk: JWK, client: TestClient
) -> None:
    claims = {"uid": "Test User", "azp": "scim-api"}
    header = {"alg": jwk.alg}
    jwt = JWT(header=header, claims=claims)
    jwt.make_signed_token(jwk)

    response = client.get("/scim/v2/Users", headers={"Authorization": f"Bearer {jwt.serialize()}"})
    assert response.status_code == 403
