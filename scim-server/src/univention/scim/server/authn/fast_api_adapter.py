# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

from typing import Any

from fastapi import Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

# Internal imports
from univention.scim.server.container import ApplicationContainer


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> Any:
        credentials: HTTPAuthorizationCredentials | None = await super().__call__(request)

        return await ApplicationContainer.authenticator().authenticate(credentials)
