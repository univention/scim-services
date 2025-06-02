# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

from typing import Any

from fastapi import APIRouter, HTTPException, Path, status
from loguru import logger
from scim2_models import EnterpriseUser, Error, Group, ListResponse, Schema, User


router = APIRouter()


def _get_schemas() -> list[Schema]:
    """Helper function to get all schemas."""
    schemas = []

    # User schema
    user_schema = User.to_schema()
    # UDM requires a last name so adept our schema accordingly
    name_attribute = next(x for x in user_schema.attributes if x.name == "name")
    name_attribute.required = True
    family_name_sub_attribute = next(x for x in name_attribute.sub_attributes if x.name == "familyName")
    family_name_sub_attribute.required = True
    schemas.append(user_schema.model_dump())

    # Group schema
    schemas.append(Group.to_schema().model_dump())

    # Add enterprise user schema
    schemas.append(EnterpriseUser.to_schema().model_dump())
    return schemas


def _get_schema_by_id(schema_id: str) -> Schema:
    """Helper function to get a specific schema by ID."""
    schemas = _get_schemas()
    for schema in schemas:
        if schema["id"] == schema_id:
            return schema

    # Create a SCIM-compliant error
    error = Error(
        status=status.HTTP_404_NOT_FOUND,
        detail="Schema '{schema_id}' not found",
        scim_type="invalidValue",
    )
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error.model_dump())


@router.get("", response_model=ListResponse[Schema], response_model_exclude_none=True)
async def get_schemas() -> Any:
    """
    Get the list of schemas supported by the SCIM service.

    Dynamically builds schema descriptions for all supported SCIM resource types
    using the built-in Schema model from scim2_models.
    """
    logger.debug("REST: Get Schemas")

    schemas = _get_schemas()

    return ListResponse[Schema](
        total_results=len(schemas),
        items_per_page=len(schemas),
        start_index=1,
        resources=schemas,
    )


@router.get("/{schema_id}", response_model=Schema, response_model_exclude_none=True)
async def get_schema_by_id(
    schema_id: str = Path(..., description="Schema ID"),
) -> Schema:
    """
    Get a specific schema by ID.

    Returns detailed information about the specified schema.
    """
    logger.debug("REST: Get Schema by ID", id=schema_id)

    try:
        return _get_schema_by_id(schema_id)
    except HTTPException:
        # Re-raise HTTPExceptions (these are already properly formatted)
        raise
    except Exception as e:
        logger.error("Error getting schema", id=schema_id, error=e)
        # Return a proper SCIM error response for server errors
        error = Error(status=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An internal server error occurred")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=error.model_dump()) from e
