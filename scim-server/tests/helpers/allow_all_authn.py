# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

from typing import Any

from fastapi import Request
from jwcrypto.jwk import JWKSet

from univention.scim.server.authn.authn import Authentication
from univention.scim.server.authn.oidc_configuration import OpenIDConnectConfiguration
from univention.scim.server.authz.authz import Authorization


class AllowAllBearerAuthentication(Authentication):
    """
    Implements bearer authentication for the SCIM API.

    This is a placeholder implementation for development purposes.
    """

    async def authenticate(self, token: str) -> dict[str, Any]:
        """
        Authenticate using HTTP Bearer authentication, allow all bearers.

        Args:
            token: The JWT token

        Returns:
            dict: User information if authentication succeeds
        """
        # Allow all tokens so no validation
        return {"username": "admin"}


class AllowAllAuthorization(Authorization):
    """
    Implements bearer authentication for the SCIM API.

    This is a placeholder implementation for development purposes.
    """

    async def authorize(self, request: Request, user: dict[str, Any]) -> bool:
        """
        Authorize a request.
        Args:
            request: The request to authorize
            user: The authenticated user's information
        Returns:
            True if authorized, False otherwise
        """
        # Allow all users
        return True


class OpenIDConnectConfigurationMock(OpenIDConnectConfiguration):
    """
    Implements well-known OpenID connect configuration.

    This is a placeholder implementation for development purposes.
    """

    def get_configuration(self, force_reload: bool = False) -> dict[str, Any]:
        """
        Get OpenID configuration from cache or from configured idp_openid_configuration_url

        Args:
            force_reload: Reload config from remote URL even if cache is available

        Returns:
            dict: OpenID configuration
        """
        return {"authorization_endpoint": "/authorize", "token_endpoint": "/token"}

    def get_jwks(self, force_reload: bool = False) -> JWKSet:
        """
        Get JWKs from cache or from OpenID configuration key "jwk_uri"

        Args:
            force_reload: Reload jwks from remote URL even if cache is available

        Returns:
            dict: JWKS from OpenID configuration
        """
        raise NotImplementedError(
            "Should never be called because auth is not checked when using the mock and AllowAllBearerAuthentication"
        )
