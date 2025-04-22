# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

from typing import Any

from fastapi import APIRouter
from scim2_models import ServiceProviderConfig
from loguru import logger

router = APIRouter()

@router.get("", response_model=ServiceProviderConfig)
async def get_service_provider_config() -> Any:
    """
    Get the service provider configuration.

    Returns information about the SCIM service provider's capabilities.
    """
    logger.debug("REST: Get ServiceProviderConfig")
    return ServiceProviderConfig(
        schemas=["urn:ietf:params:scim:schemas:core:2.0:ServiceProviderConfig"],
        documentation_uri="https://docs.univention.de/scim-api/",
        patch={"supported": True},
        bulk={"supported": False},
        filter={"supported": True, "max_results": 100},  # Note: document only 'eq' is supported
        change_password={"supported": True},
        sort={"supported": False},
        etag={"supported": False},
        authentication_schemes=[
            {
                "name": "OAuth Bearer Token",
                "description": "Authentication scheme using the OAuth Bearer Token Standard",
                "spec_uri": "http://www.rfc-editor.org/info/rfc6750",
                "documentation_uri": "https://docs.univention.de/scim-api/auth/oauth.html",
                "type": "oauthbearertoken",
                "primary": True,
            }
        ],
    )
