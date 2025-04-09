# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH
from abc import ABC, abstractmethod
from typing import Any

from jwcrypto.jwk import JWKSet


class OpenIDConnectConfiguration(ABC):
    """
    Implements well-known OpenID connect configuration.

    Gets the OpenID connection settings from a well-known URL
    """

    @abstractmethod
    def get_configuration(self, force_reload: bool = False) -> dict[str, Any]:
        """
        Get OpenID configuration from cache or from configured idp_openid_configuration_url

        Args:
            force_reload: Reload config from remote URL even if cache is available

        Returns:
            dict: OpenID configuration
        """
        pass

    @abstractmethod
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
        pass
