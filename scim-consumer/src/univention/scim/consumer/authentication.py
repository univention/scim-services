# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

import base64
import binascii
import json
import time
from collections.abc import Generator

import httpx
from loguru import logger
from pydantic import AnyHttpUrl
from pydantic_settings import BaseSettings


class GetTokenError(Exception): ...


class AuthenticatorSettings(BaseSettings):
    scim_oidc_token_url: AnyHttpUrl
    scim_client_id: str
    scim_client_secret: str


class Authenticator(httpx.Auth):
    _access_token: str | None = None

    def __init__(self, settings: AuthenticatorSettings, http_client: httpx.Client | None = None) -> None:
        self._settings = settings
        self._client = http_client or httpx.Client()

    def _valid_token(self) -> str | None:
        if not self._access_token:
            return None
        try:
            parts = self._access_token.split(".")
            payload_b64 = parts[1]
            payload_b64 += "=" * (-len(payload_b64) % 4)
            payload_bytes = base64.urlsafe_b64decode(payload_b64)
            claims = json.loads(payload_bytes)
            expiery_time = claims["exp"]
        except (IndexError, binascii.Error, json.JSONDecodeError, KeyError) as error:
            logger.warning("Could not parse the existing JWT AccessToken and evaluate the expiery time: %r", error)
            return None
        if time.time() >= expiery_time:
            logger.info("existing JWT is expired")
            return None

        return self._access_token

    def _authenticate(self) -> str:
        data = {
            "grant_type": "client_credentials",
            "client_id": self._settings.scim_client_id,
            "client_secret": self._settings.scim_client_secret,
        }
        try:
            response = self._client.post(
                url=str(self._settings.scim_oidc_token_url),
                data=data,
                headers={"Accept": "application/json"},
            )
            response.raise_for_status()
        except (httpx.RequestError, httpx.HTTPStatusError) as error:
            raise GetTokenError("Getting the access token from the IDP failed") from error

        try:
            payload = response.json()
        except json.JSONDecodeError as err:
            raise GetTokenError("token endpoint returned invalid JSON") from err

        token = payload.get("access_token")
        if not token:
            description = payload.get("error_description") or payload.get("error") or "<none>"
            raise GetTokenError(f"no access_token in response: {description!r}")

        self._access_token = token
        return token

    def get_token(self) -> str:
        if token := self._valid_token():
            return token
        return self._authenticate()

    def auth_flow(self, request: httpx.Request) -> Generator[httpx.Request, httpx.Response, None]:
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
