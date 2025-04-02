# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH
from fastapi import APIRouter, Security

# Internal imports
from univention.scim.server.authn.fast_api_adapter import JWTBearer
from univention.scim.server.container import ApplicationContainer
from univention.scim.server.rest import groups, service_provider, users


def get_api_router(container: ApplicationContainer) -> APIRouter:
    # Create main API router
    router = APIRouter(dependencies=[Security(JWTBearer())]) if container.settings().auth_enabled else APIRouter()

    # Include sub-routers
    router.include_router(users.get_api_router(container), prefix="/Users", tags=["Users"])
    router.include_router(groups.get_api_router(container), prefix="/Groups", tags=["Groups"])
    router.include_router(
        service_provider.get_api_router(), prefix="/ServiceProviderConfig", tags=["ServiceProviderConfig"]
    )

    return router
