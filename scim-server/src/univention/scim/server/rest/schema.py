# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

from typing import Annotated

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException, Path, status
from loguru import logger
from scim2_models import Error, ListResponse, Schema

from univention.scim.server.container import ApplicationContainer
from univention.scim.server.model_service.load_schemas import LoadSchemas


router = APIRouter()


def _get_schema_by_id(schema_loader: LoadSchemas, schema_id: str) -> Schema:
    """Helper function to get a specific schema by ID."""
    schemas = schema_loader.get_supported_schemas()
    for schema in schemas:
        if schema.id == schema_id:
            return schema

    # Create a SCIM-compliant error
    error = Error(
        status=status.HTTP_404_NOT_FOUND,
        detail="Schema '{schema_id}' not found",
        scim_type="invalidValue",
    )
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error.model_dump())


@router.get("", response_model=ListResponse[Schema], response_model_exclude_none=True)
@inject
async def get_schemas(
    schema_loader: Annotated[LoadSchemas, Depends(Provide[ApplicationContainer.schema_loader])],
) -> ListResponse[Schema]:
    """
    Get the list of schemas supported by the SCIM service.

    Dynamically builds schema descriptions for all supported SCIM resource types
    using the built-in Schema model from scim2_models.
    """
    logger.debug("REST: Get Schemas")

    schemas = schema_loader.get_supported_schemas()

    return ListResponse[Schema](
        total_results=len(schemas),
        items_per_page=len(schemas),
        start_index=1,
        resources=[x.model_dump() for x in schemas],
    )


@router.get("/{schema_id}", response_model=Schema, response_model_exclude_none=True)
@inject
async def get_schema_by_id(
    schema_loader: Annotated[LoadSchemas, Depends(Provide[ApplicationContainer.schema_loader])],
    schema_id: str = Path(..., description="Schema ID"),
) -> Schema:
    """
    Get a specific schema by ID.

    Returns detailed information about the specified schema.
    """
    logger.debug("REST: Get Schema by ID", id=schema_id)

    try:
        return _get_schema_by_id(schema_loader, schema_id).model_dump()
    except HTTPException:
        # Re-raise HTTPExceptions (these are already properly formatted)
        raise
    except Exception as e:
        logger.error("Error getting schema", id=schema_id, error=e)
        # Return a proper SCIM error response for server errors
        error = Error(status=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An internal server error occurred")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=error.model_dump()) from e
