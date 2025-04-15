# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

from typing import Any

import requests
from jwcrypto.common import JWException
from jwcrypto.jwk import JWKSet
from loguru import logger

from univention.scim.server.authn.oidc_configuration import OpenIDConnectConfiguration
from univention.scim.server.config import AuthenticatorConfig


class OpenIDConnectConfigurationImpl(OpenIDConnectConfiguration):
    """
    Implements well-known OpenID connect configuration.

    Gets the OpenID connection settings from a well-known URL
    """

    def __init__(self, config: AuthenticatorConfig) -> None:
        self.config = config
        self.oidc_config: dict[str, Any] | None = None
        self.jwks: JWKSet | None = None

    def get_configuration(self, force_reload: bool = False) -> dict[str, Any]:
        """
        Get OpenID configuration from cache or from configured idp_openid_configuration_url

        Args:
            force_reload: Reload config from remote URL even if cache is available

        Returns:
            dict: OpenID configuration

        Raises:
            requests.exceptions.RequestException: If getting configuration or jwks fails
        """
        if not force_reload and self.oidc_config:
            return self.oidc_config

        logger.info("Getting OpenID connect configuration", url=self.config.idp_openid_configuration_url)
        try:
            self.oidc_config = requests.get(self.config.idp_openid_configuration_url).json()
        except requests.exceptions.RequestException as e:
            logger.error(
                "Failed to get OpenID connect configuration", url=self.config.idp_openid_configuration_url, error=e
            )
            raise

        if (
            not self.oidc_config
            or not isinstance(self.oidc_config, dict)
            or "authorization_endpoint" not in self.oidc_config
            or "token_endpoint" not in self.oidc_config
            or "jwks_uri" not in self.oidc_config
            or "id_token_signing_alg_values_supported" not in self.oidc_config
        ):
            logger.error("Invalid OpenID connect configuration", url=self.config.idp_openid_configuration_url)
            raise ValueError("Invalid OpenID connect configuration")

        return self.oidc_config

    def get_jwks(self, force_reload: bool = False) -> JWKSet:
        """
        Get JWKs from cache or from OpenID configuration key "jwk_uri"

        Args:
            force_reload: Reload jwks from remote URL even if cache is available

        Returns:
            dict: JWKS from OpenID configuration

        Raises:
            requests.exceptions.RequestException: If getting configuration or jwks fails
            KeyError: If mandatory key is not available in returned OpenID configuration
            JWException: If parsing jwks fails
        """
        if not force_reload and self.jwks:
            return self.jwks

        configuration = self.get_configuration()
        if "jwks_uri" not in configuration:
            logger.error("No JWK information in OpenID configuration", url=self.config.idp_openid_configuration_url)
            raise KeyError("jwks_uri")

        jwks_url = configuration["jwks_uri"]
        logger.info("Getting OpenID connect jwks", url=jwks_url)
        try:
            self.jwks = JWKSet.from_json(requests.get(jwks_url).text)
        except requests.exceptions.RequestException:
            logger.error("Failed to get jwks", url=configuration["jwks_uri"])
            raise
        except JWException:
            logger.error("Failed to read jwks", url=configuration["jwks_uri"])
            raise

        return self.jwks
