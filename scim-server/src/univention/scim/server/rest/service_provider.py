# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH
from typing import Any

from fastapi import APIRouter


router = APIRouter()


@router.get("/.well-known/scim-configuration")
async def get_service_provider_config() -> Any:
    # This is a dummy implementation
    return {
        "schemas": ["urn:ietf:params:scim:schemas:core:2.0:ServiceProviderConfig"],
        "documentationUri": "https://docs.univention.de/",
        "patch": {"supported": True},
        "bulk": {"supported": False},
        "filter": {"supported": True, "maxResults": 100},
        "changePassword": {"supported": True},
        "sort": {"supported": True},
        "etag": {"supported": False},
        "authenticationSchemes": [
            {
                "type": "oauth2",
                "name": "OAuth 2.0",
                "description": "OAuth 2.0 Authentication Scheme",
                "specUri": "https://tools.ietf.org/html/rfc6749",
                "documentationUri": "https://docs.univention.de/",
            }
        ],
    }
