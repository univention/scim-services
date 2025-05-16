# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

from typing import Any

from fastapi import Request
from fastapi.security import OAuth2AuthorizationCodeBearer

from univention.scim.server.authn.authn import Authentication
from univention.scim.server.authz.authz import Authorization


class FastAPIAuthAdapter(OAuth2AuthorizationCodeBearer):
    def __init__(
        self, configuration: dict[str, Any], authentication: Authentication, authorization: Authorization
    ) -> None:
        super().__init__(
            authorizationUrl=configuration["authorization_endpoint"],
            tokenUrl=configuration["token_endpoint"],
            scopes={"openid": "scope for openid"},
        )
        self.authentication = authentication
        self.authorization = authorization

    async def __call__(self, request: Request) -> Any:
        token: str | None = await super().__call__(request)

        user_data = await self.authentication.authenticate(token)
        await self.authorization.authorize(request, user_data)

        return user_data
