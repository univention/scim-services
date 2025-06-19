# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

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


class Authenticator:
    access_token: str | None = None

    def __init__(
        self, settings: AuthenticatorSettings | None, keycloak_adapter: type[KeycloakOpenID] = KeycloakOpenID
    ) -> None:
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
