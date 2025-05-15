# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH
from typing import Annotated

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException, Path, Request, status
from loguru import logger

# Import models from scim2-models
from scim2_models import ListResponse, Meta, ResourceType, SchemaExtension

from univention.scim.server.config import ApplicationSettings
from univention.scim.server.container import ApplicationContainer


router = APIRouter()


def _get_resource_type(request: Request, settings: ApplicationSettings, resource_id: str) -> ResourceType:
    """Helper function to get a specific resource type by ID."""
    base_url = str(request.base_url).rstrip("/") + settings.api_prefix.rstrip("/")

    if resource_id == "User":
        return ResourceType(
            id="User",
            name="User",
            description="User Account",
            endpoint="/Users",  # Relative endpoint
            schema_="urn:ietf:params:scim:schemas:core:2.0:User",
            schema_extensions=[
                SchemaExtension(
                    schema_="urn:ietf:params:scim:schemas:extension:enterprise:2.0:User",
                    required=False,
                )
            ],
            meta=Meta(
                location=f"{base_url}/ResourceTypes/User",
                resourceType="ResourceType",
            ),
        )
    elif resource_id == "Group":
        return ResourceType(
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
    else:
        # Create an exception with proper SCIM error format
        error_detail = {
            "schemas": ["urn:ietf:params:scim:api:messages:2.0:Error"],
            "status": str(status.HTTP_404_NOT_FOUND),
            "detail": f"Resource type '{resource_id}' not found",
            "scimType": "invalidValue",
        }
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error_detail)


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
    user_resource_type = _get_resource_type(request, settings, "User")
    group_resource_type = _get_resource_type(request, settings, "Group")

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


@router.get("/{resource_id}", response_model=ResourceType, response_model_exclude_none=True)
@inject
async def get_resource_type_by_id(
    request: Request,
    settings: Annotated[ApplicationSettings, Depends(Provide[ApplicationContainer.settings])],
    resource_id: str = Path(..., description="Resource type ID"),
) -> ResourceType:
    """
    Get a specific resource type by ID.

    Returns detailed information about the specified resource type.
    """
    try:
        return _get_resource_type(request, settings, resource_id)
    except HTTPException:
        # Re-raise HTTPExceptions (these are already properly formatted)
        raise
    except Exception as e:
        logger.error("Error getting resource type", id=resource_id, error=e)
        # Return a proper SCIM error response for server errors
        error_detail = {
            "schemas": ["urn:ietf:params:scim:api:messages:2.0:Error"],
            "status": str(status.HTTP_500_INTERNAL_SERVER_ERROR),
            "detail": "An internal server error occurred",
        }
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=error_detail) from e
