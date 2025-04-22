# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

from typing import Any

from fastapi import Request
from fastapi.security import OAuth2AuthorizationCodeBearer

from univention.scim.server.container import ApplicationContainer


class FastAPIAuthAdapter(OAuth2AuthorizationCodeBearer):
    def __init__(self, configuration: dict[str, Any]) -> None:
        super().__init__(
            authorizationUrl=configuration["authorization_endpoint"],
            tokenUrl=configuration["token_endpoint"],
            scopes={"openid": "scope for openid"},
        )

    async def __call__(self, request: Request) -> Any:
        token: str | None = await super().__call__(request)

        authenticator = ApplicationContainer.authenticator()
        return await authenticator.authenticate(token)
