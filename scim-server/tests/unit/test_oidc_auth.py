# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

import time
from collections.abc import Callable, Generator
from contextlib import _GeneratorContextManager, contextmanager, nullcontext
from typing import Any

import pytest
from fastapi.testclient import TestClient
from jwcrypto.jwk import JWK
from jwcrypto.jwt import JWT
from pytest_httpserver.httpserver import HTTPServer

from univention.scim.server.authn.authn_impl import OpenIDConnectAuthentication
from univention.scim.server.authn.oidc_configuration_impl import OpenIDConnectConfigurationImpl
from univention.scim.server.authz.authz_impl import AllowAudience
from univention.scim.server.config import AuthenticatorConfig
from univention.scim.server.container import ApplicationContainer


TOKEN_EXPIRY_SECONDS = 120
RSA_KEY_SIZE = 2048


class TestAuthBase:
    _test__ = False
    enable_authz = False
    register_oidc_configuration_url = True

    @pytest.fixture
    def jwk(self) -> JWK:
        return JWK.generate(kty="RSA", size=RSA_KEY_SIZE, alg="RS256", use="sig", kid="good")

    # Override after_setup tets fixture to inject our override
    @pytest.fixture
    def after_setup(self, jwk: JWK, httpserver: HTTPServer) -> Callable[[], _GeneratorContextManager[Any, None, None]]:
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

            if self.register_oidc_configuration_url:
                httpserver.expect_request(oidc_configuration_url).respond_with_json(oidc_configuration)

            httpserver.expect_request(jwks_uri).respond_with_json(
                {"keys": [jwk.export(private_key=False, as_dict=True)]}
            )

            oidc_configuration_obj = OpenIDConnectConfigurationImpl(
                AuthenticatorConfig(idp_openid_configuration_url=httpserver.url_for(oidc_configuration_url))
            )

            with (
                ApplicationContainer.authenticator.override(
                    OpenIDConnectAuthentication(oidc_configuration_obj, "scim-api")
                ),
                ApplicationContainer.oidc_configuration.override(oidc_configuration_obj),
                ApplicationContainer.authorization.override(AllowAudience("scim-access"))
                if self.enable_authz
                else nullcontext(),
            ):
                yield

        return override_authenticator

    def check_response(self, client: TestClient, jwk: JWK, jwt: JWT, expected_response_code: int) -> None:
        jwt.make_signed_token(jwk)

        response = client.get("/scim/v2/Users", headers={"Authorization": f"Bearer {jwt.serialize()}"})
        assert response.status_code == expected_response_code


class TestAuthn(TestAuthBase):
    _test__ = True

    @pytest.mark.xfail(strict=True, raises=ValueError)
    def test_oidc_invalid_configuration(self, request: Any, jwk: JWK, httpserver: HTTPServer) -> None:
        oidc_configuration = {
            "authorization_endpoint": httpserver.url_for("/authorize"),
            "token_endpoint": httpserver.url_for("/token"),
        }

        httpserver.expect_request("/.well-known/openid-configuration").respond_with_json(oidc_configuration)

        self.register_oidc_configuration_url = False
        # setting up the client should throw an exception because oidc_configuration is invalid
        request.getfixturevalue("client")

    @pytest.mark.xfail(strict=True, raises=ValueError)
    def test_oidc_no_route(self, request: Any, jwk: JWK, httpserver: HTTPServer) -> None:
        self.register_oidc_configuration_url = False
        # setting up the client should throw an exception because oidc configuration URL is not accessible
        request.getfixturevalue("client")

    def test_oidc_auth(self, jwk: JWK, client: TestClient) -> None:
        claims = {"aud": "scim-access", "azp": "scim-api", "exp": int(time.time()) + TOKEN_EXPIRY_SECONDS}
        header = {"alg": jwk.alg}
        jwt = JWT(header=header, claims=claims)
        self.check_response(client, jwk, jwt, 200)

    def test_oidc_auth_token_expired(self, jwk: JWK, client: TestClient) -> None:
        claims = {"aud": "scim-access", "azp": "scim-api", "exp": int(time.time()) - TOKEN_EXPIRY_SECONDS}
        header = {"alg": jwk.alg}
        jwt = JWT(header=header, claims=claims)
        self.check_response(client, jwk, jwt, 403)

    def test_oidc_auth_wrong_client_id(self, jwk: JWK, client: TestClient) -> None:
        claims = {"aud": "scim-access", "azp": "not-scim-api", "exp": int(time.time()) + TOKEN_EXPIRY_SECONDS}
        header = {"alg": jwk.alg}
        jwt = JWT(header=header, claims=claims)
        self.check_response(client, jwk, jwt, 403)

    def test_oidc_auth_wrong_signature(self, jwk: JWK, client: TestClient) -> None:
        claims = {"aud": "scim-access", "azp": "scim-api", "exp": int(time.time()) + TOKEN_EXPIRY_SECONDS}
        header = {"alg": jwk.alg}
        jwt = JWT(header=header, claims=claims)

        test_key = JWK.generate(kty="RSA", size=RSA_KEY_SIZE, alg="RS256", use="sig", kid="good")
        self.check_response(client, test_key, jwt, 403)

    def test_oidc_auth_missing_kid(self, jwk: JWK, client: TestClient) -> None:
        claims = {"aud": "scim-access", "azp": "scim-api", "exp": int(time.time()) + 120}
        header = {"alg": jwk.alg}
        jwt = JWT(header=header, claims=claims)

        test_key = JWK.generate(kty="RSA", size=RSA_KEY_SIZE, alg="RS256", use="sig", kid="fail")
        self.check_response(client, test_key, jwt, 403)

    def test_oidc_auth_mandatory_claim_aud_missing(self, jwk: JWK, client: TestClient) -> None:
        claims = {"azp": "scim-api", "exp": int(time.time()) + TOKEN_EXPIRY_SECONDS}
        header = {"alg": jwk.alg}
        jwt = JWT(header=header, claims=claims)
        self.check_response(client, jwk, jwt, 403)

    def test_oidc_auth_mandatory_claim_azp_missing(self, jwk: JWK, client: TestClient) -> None:
        claims = {"aud": "scim-access", "exp": int(time.time()) + TOKEN_EXPIRY_SECONDS}
        header = {"alg": jwk.alg}
        jwt = JWT(header=header, claims=claims)
        self.check_response(client, jwk, jwt, 403)

    def test_oidc_auth_mandatory_claim_exp_missing(self, jwk: JWK, client: TestClient) -> None:
        claims = {"aud": "scim-access", "azp": "scim-api"}
        header = {"alg": jwk.alg}
        jwt = JWT(header=header, claims=claims)
        self.check_response(client, jwk, jwt, 403)


class TestAuthz(TestAuthBase):
    _test__ = True
    enable_authz = True

    def test_valid_audience(self, jwk: JWK, client: TestClient) -> None:
        claims = {"aud": "scim-access", "azp": "scim-api", "exp": int(time.time()) + TOKEN_EXPIRY_SECONDS}
        header = {"alg": jwk.alg}
        jwt = JWT(header=header, claims=claims)
        self.check_response(client, jwk, jwt, 200)

    def test_invalid_audience(self, jwk: JWK, client: TestClient) -> None:
        claims = {"aud": "scim-no-access", "azp": "scim-api", "exp": int(time.time()) + TOKEN_EXPIRY_SECONDS}
        header = {"alg": jwk.alg}
        jwt = JWT(header=header, claims=claims)
        self.check_response(client, jwk, jwt, 403)
