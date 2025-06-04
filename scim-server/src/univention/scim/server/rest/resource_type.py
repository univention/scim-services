# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH
from typing import Annotated

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException, Path, status
from loguru import logger

# Import models from scim2-models
from scim2_models import Error, ListResponse, ResourceType

from univention.scim.server.container import ApplicationContainer
from univention.scim.server.model_service.load_schemas import LoadSchemas


router = APIRouter()


def _get_resource_type_by_id(schema_loader: LoadSchemas, resource_id: str) -> ResourceType:
    """Helper function to get a specific schema by ID."""
    resource_types = schema_loader.get_resource_types()
    for resource_type in resource_types:
        if resource_type.id == resource_id:
            return resource_type

    # Create a SCIM-compliant error
    error = Error(
        status=status.HTTP_404_NOT_FOUND,
        detail="Schema '{resource_id}' not found",
        scim_type="invalidValue",
    )
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error.model_dump())


@router.get("", response_model=ListResponse[ResourceType], response_model_exclude_none=True)
@inject
async def get_resource_types(
    schema_loader: Annotated[LoadSchemas, Depends(Provide[ApplicationContainer.schema_loader])],
) -> ListResponse[ResourceType]:
    """
    Get the list of resource types supported by the SCIM service.

    Returns a ListResponse containing User and Group resource types based on scim2-models.
    """
    # Create the list of resources
    resource_types = schema_loader.get_resource_types()

    # Construct and return the ListResponse object
    return ListResponse[ResourceType](
        total_results=len(resource_types),
        items_per_page=len(resource_types),
        start_index=1,
        resources=[x.model_dump() for x in resource_types],
    )


@router.get("/{resource_id}", response_model=ResourceType, response_model_exclude_none=True)
@inject
async def get_resource_type_by_id(
    schema_loader: Annotated[LoadSchemas, Depends(Provide[ApplicationContainer.schema_loader])],
    resource_id: str = Path(..., description="Resource type ID"),
) -> ResourceType:
    """
    Get a specific resource type by ID.

    Returns detailed information about the specified resource type.
    """
    try:
        return _get_resource_type_by_id(schema_loader, resource_id)
    except HTTPException:
        # Re-raise HTTPExceptions (these are already properly formatted)
        raise
    except Exception as e:
        logger.error("Error getting resource type", id=resource_id, error=e)
        error = Error(status=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An internal server error occurred")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=error.model_dump()) from e
