# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

import json
from typing import Any

from fastapi import HTTPException, status
from jwcrypto.common import JWKeyNotFound
from jwcrypto.jwk import JWKSet
from jwcrypto.jwt import JWT, JWTMissingClaim
from loguru import logger

from univention.scim.server.authn.authn import Authentication
from univention.scim.server.authn.oidc_configuration import OpenIDConnectConfiguration


class OpenIDConnectAuthentication(Authentication):
    """
    Implements bearer authentication for the SCIM API.

    Validates an open id connect token against the given open id connect configuration.
    """

    def __init__(self, oidc_configuration: OpenIDConnectConfiguration, client_id: str):
        self.oidc_configuration = oidc_configuration
        self.client_id = client_id

    def _validate_token(self, token: str, jwks: JWKSet, algs: str, retry: bool) -> JWT:
        """
        Validate a JWT token

        If key is not found in key set, redownload key set from oidc configuration once
        to be sure keys have not changed since initial fetching.

        Args:
            token: The JWT token to validate
            jwks: A JWKSet of available keys
            algs: A list of supported algorithms
            retry: If true, reload JWKSet from remote URL if kid is not found in set

        Returns:
            JWT: A valid JWT

        Raises:
            HTTPException: If validation fails
        """
        try:
            return JWT(jwt=token, key=jwks, algs=algs, check_claims={"uid": None, "azp": self.client_id})
        except JWKeyNotFound as e:
            if not retry:
                logger.error("Token validation failed: Invalid signature", error=e)
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid token.") from e

            try:
                jwks = self.oidc_configuration.get_jwks(True)
            except Exception:
                logger.error("Token validation failed: Invalid OpenID connect configuration")
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN, detail="Invalid OpenID connect configuration."
                ) from e

            return self._validate_token(token, jwks, algs, False)
        except JWTMissingClaim as e:
            logger.error("Token validation failed: Mandatory claim missing", error=e)
        except Exception:
            logger.error("Token validation failed: Generic error")

        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid token.")

    async def authenticate(self, token: str) -> dict[str, Any]:
        """
        Authenticate using HTTP Bearer authentication, allow all bearers.

        Args:
            token: The JWT token

        Returns:
            dict: User information if authentication succeeds

        Raises:
            HTTPException: If authentication fails
        """
        try:
            configuration = self.oidc_configuration.get_configuration()
            if "id_token_signing_alg_values_supported" not in configuration:
                logger.error("Token validation failed: Invalid OpenID connect configuration")
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN, detail="Invalid OpenID connect configuration."
                )

            jwks = self.oidc_configuration.get_jwks()
        except Exception as e:
            logger.error("Token validation failed: Invalid OpenID connect configuration")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Invalid OpenID connect configuration."
            ) from e

        jwt = self._validate_token(token, jwks, configuration["id_token_signing_alg_values_supported"], True)
        jwt_claims = json.loads(jwt.claims)

        return {"username": jwt_claims["uid"]}
