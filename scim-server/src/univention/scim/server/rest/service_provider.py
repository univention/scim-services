# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH
from typing import Any

from fastapi import APIRouter
from scim2_models import ServiceProviderConfig


def get_api_router() -> APIRouter:
    router = APIRouter()

    @router.get("", response_model=ServiceProviderConfig)
    async def get_service_provider_config() -> Any:
        """
        Get the service provider configuration.

        Returns information about the SCIM service provider's capabilities.
        """
        return ServiceProviderConfig(
            schemas=["urn:ietf:params:scim:schemas:core:2.0:ServiceProviderConfig"],
            documentation_uri="https://docs.univention.de/scim-api/",
            patch={"supported": True},
            bulk={"supported": False},
            filter={"supported": True, "max_results": 100},
            change_password={"supported": False},
            sort={"supported": True},
            etag={"supported": False},
            authentication_schemes=[
                {
                    "name": "OAuth Bearer Token",
                    "description": "Authentication using OAuth 2.0 Bearer Token",
                    "spec_uri": "https://oauth.net/2/",
                    "type": "oauthbearertoken",
                    "primary": True,
                }
            ],
        )

    return router
