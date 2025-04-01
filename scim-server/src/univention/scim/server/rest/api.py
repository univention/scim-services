# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH
from fastapi import APIRouter, Security

# Internal imports
from univention.scim.server.authn.fast_api_adapter import JWTBearer
from univention.scim.server.container import ApplicationContainer
from univention.scim.server.rest import groups, service_provider, users


def get_api_router() -> APIRouter:
    # Create main API router
    if ApplicationContainer.settings().auth_enabled:
        router = APIRouter(dependencies=[Security(JWTBearer())])
    else:
        router = APIRouter()

    # Include sub-routers
    router.include_router(users.router, prefix="/Users", tags=["Users"])
    router.include_router(groups.router, prefix="/Groups", tags=["Groups"])
    router.include_router(service_provider.router, prefix="/ServiceProviderConfig", tags=["ServiceProviderConfig"])

    return router
