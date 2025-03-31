# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH
from fastapi import APIRouter, Security
from univention.scim.server.rest import groups, service_provider, users
from univention.scim.server.authn.fast_api_adapter import JWTBearer


# Create main API router
router = APIRouter(dependencies=[Security(JWTBearer())])

# Include sub-routers
router.include_router(users.router, prefix="/Users", tags=["Users"])
router.include_router(groups.router, prefix="/Groups", tags=["Groups"])
router.include_router(service_provider.router, prefix="/ServiceProviderConfig", tags=["ServiceProviderConfig"])
