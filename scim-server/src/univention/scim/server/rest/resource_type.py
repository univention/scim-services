# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH
from typing import Annotated

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Request
from loguru import logger

# Import models from scim2-models
# Import ListResponse model
from scim2_models import ListResponse, Meta, ResourceType, SchemaExtension

from univention.scim.server.config import ApplicationSettings
from univention.scim.server.container import ApplicationContainer


router = APIRouter()


@router.get("", response_model=ListResponse[ResourceType], response_model_exclude_none=True)
@inject
async def get_resource_types(
    request: Request,
    settings: Annotated[ApplicationSettings, Depends(Provide[ApplicationContainer.settings])],
) -> ListResponse[ResourceType]:
    """
    Get the list of resource types supported by the SCIM service.

    Returns a ListResponse containing User and Group resource types based on scim2-models.
    """
    logger.debug("REST: Get ResourceTypes")

    base_url = str(request.base_url).rstrip("/") + settings.api_prefix.rstrip("/")

    user_resource_type = ResourceType(
        id="User",
        name="User",
        description="User Account",
        endpoint="/Users",  # Relative endpoint
        schema_="urn:ietf:params:scim:schemas:core:2.0:User",
        schema_extensions=[
            SchemaExtension(
                schema_="urn:ietf:params:scim:schemas:extension:enterprise:2.0:User",
                required=True,
            )
        ],
        meta=Meta(
            location=f"{base_url}/ResourceTypes/User",
            resourceType="ResourceType",
        ),
    )

    group_resource_type = ResourceType(
        id="Group",
        name="Group",
        description="Group",
        endpoint="/Groups",  # Relative endpoint
        schema_="urn:ietf:params:scim:schemas:core:2.0:Group",
        schema_extensions=[],
        meta=Meta(
            location=f"{base_url}/ResourceTypes/Group",
            resourceType="ResourceType",
        ),
    )

    # Create the list of resources
    resources = [user_resource_type, group_resource_type]
    total_results = len(resources)

    # Construct and return the ListResponse object
    return ListResponse[ResourceType](
        total_results=total_results,
        items_per_page=total_results,  # Assuming no pagination for this endpoint
        start_index=1,
        resources=resources,
    )
