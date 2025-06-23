# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

from collections.abc import Generator

from httpx import Auth, Request, Response
from jwcrypto.jwt import JWTExpired
from keycloak import KeycloakAuthenticationError, KeycloakError, KeycloakGetError, KeycloakOpenID
from loguru import logger
from pydantic import AnyHttpUrl
from pydantic_settings import BaseSettings


class GetTokenError(Exception): ...


class AuthenticatorSettings(BaseSettings):
    scim_idp_base_url: AnyHttpUrl
    scim_client_id: str
    scim_client_secret: str
    scim_idp_realm: str
    scim_idp_audience: str


class Authenticator(Auth):
    access_token: str | None = None

    def __init__(
        self, settings: AuthenticatorSettings | None = None, keycloak_adapter: type[KeycloakOpenID] = KeycloakOpenID
    ) -> None:
        # TODO: remove the or path
        self.settings = settings or AuthenticatorSettings()
        self.keycloak = keycloak_adapter(
            server_url=str(self.settings.scim_idp_base_url),
            realm_name=self.settings.scim_idp_realm,
            client_id=self.settings.scim_client_id,
            client_secret_key=self.settings.scim_client_secret,
        )

    def _valid_token(self) -> str | None:
        if not self.access_token:
            return None
        try:
            self.keycloak.decode_token(self.access_token)
        except JWTExpired as error:
            logger.info("existing JWT is expired", "error", error)
            return None
        return self.access_token

    def _authenticate(self) -> str:
        try:
            token_response = self.keycloak.token(grant_type="client_credentials")
            self.access_token = token_response.get("access_token")
        except (KeycloakAuthenticationError, KeycloakError, KeycloakGetError) as err:
            raise GetTokenError("Getting the access token from Keycloak failed") from err
        if not self.access_token:
            error_response = token_response.get("error_description") or token_response.get("error")
            raise GetTokenError(f"No access token in authentication response: {error_response!r}")
        return self.access_token

    def get_token(self) -> str:
        if token := self._valid_token():
            return token
        return self._authenticate()

    def auth_flow(self, request: Request) -> Generator[Request, Response, None]:
        """
        Generator plugin for the httpx.Client class

        Ensures that the request is executed with a valid token.
        If the request returns a 401 Unauthorized,
        a new token will be explicitly fetched and the request retried.

        This covers scenarios where the account configuration has been updated
        (to fix a configuration mistake) But the old token has not yet expired.
        """
        request.headers["Authorization"] = f"Bearer {self.get_token()}"

        response = yield request
        if response.status_code != 401:
            return
        request.headers["Authorization"] = f"Bearer {self._authenticate()}"
