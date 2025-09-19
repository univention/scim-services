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

    def _parse_token_claims(self) -> dict | None:
        """Parse claims from either JWT or plain JSON token format."""
        if not self._access_token:
            return None

        # Try parsing as JWT first
        claims = self._parse_jwt_claims()
        if claims is not None:
            return claims

        # Fallback to plain JSON parsing
        try:
            return json.loads(self._access_token)
        except json.JSONDecodeError as error:
            logger.warning(
                "Could not parse the existing AccessToken as JWT or plain JSON and evaluate the expiry time: %r",
                error,
            )
            return None

    def _parse_jwt_claims(self) -> dict | None:
        """Parse claims from JWT token format."""
        try:
            parts = self._access_token.split(".")
            if len(parts) != 3:  # Valid JWT should have 3 parts: header.payload.signature
                return None

            payload_b64 = parts[1]
            # Restore base64 padding that may have been stripped during JWT encoding
            payload_b64 += "=" * (-len(payload_b64) % 4)
            payload_bytes = base64.urlsafe_b64decode(payload_b64)
            return json.loads(payload_bytes.decode("utf-8"))
        except (IndexError, binascii.Error, json.JSONDecodeError, UnicodeDecodeError):
            return None

    def _valid_token(self) -> str | None:
        if not self._access_token:
            return None

        claims = self._parse_token_claims()
        if claims is None:
            return None

        # Check expiry if present, but be optimistic if missing
        expiry_time = claims.get("exp")
        if expiry_time is not None:
            try:
                # Convert to float to handle both numeric and string exp claims
                expiry_time = float(expiry_time)
                if time.time() >= expiry_time:
                    logger.info("existing AccessToken is expired")
                    return None
            except (ValueError, TypeError) as error:
                logger.warning("AccessToken has invalid 'exp' claim format: %r", error)
                return None
        else:
            # No exp claim - be optimistic and pass through the token
            logger.debug("AccessToken does not contain 'exp' claim, passing through optimistically")

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

        token: str = payload.get("access_token")
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
