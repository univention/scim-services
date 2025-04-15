# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

from typing import Any

from fastapi import Request
from fastapi.security import OAuth2AuthorizationCodeBearer

from univention.scim.server.authn.authn import Authentication
from univention.scim.server.container import ApplicationContainer


#
# We don't want network access at initialization time, but we must initialize super().
# So, we create (and cache) the object at runtime.
#


class RealFastAPIAuthAdapter(OAuth2AuthorizationCodeBearer):
    def __init__(self, authenticator: Authentication, configuration: dict[str, Any]) -> None:
        self.authenticator = authenticator
        super().__init__(
            authorizationUrl=configuration["authorization_endpoint"],
            tokenUrl=configuration["token_endpoint"],
            scopes={"openid": "scope for openid"},
        )

    async def __call__(self, request: Request) -> Any:
        token: str | None = await super().__call__(request)
        return await self.authenticator.authenticate(token)


class FastAPIAuthAdapter(OAuth2AuthorizationCodeBearer):
    def __init__(self) -> None:
        self.real_auth: RealFastAPIAuthAdapter | None = None

    async def __call__(self, request: Request) -> Any:
        if not self.real_auth:
            authenticator = ApplicationContainer.authenticator()
            oidc_configuration = ApplicationContainer.oidc_configuration()
            configuration = oidc_configuration.get_configuration()
            self.real_auth = RealFastAPIAuthAdapter(authenticator, configuration)

        return await self.real_auth(request)
