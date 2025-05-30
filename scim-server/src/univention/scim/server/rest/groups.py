# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

from typing import Annotated, Any

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Body, Depends, HTTPException, Path, Query, Response, status
from loguru import logger
from scim2_models import Group, ListResponse

from univention.scim.server.container import ApplicationContainer
from univention.scim.server.domain.group_service import GroupService
from univention.scim.transformation.exceptions import MappingError


router = APIRouter()


@router.get("", response_model=ListResponse[Group])
@inject
async def list_groups(
    group_service: Annotated[GroupService, Depends(Provide[ApplicationContainer.group_service])],
    filter: str | None = Query(None, description="SCIM filter expression"),
    start_index: int = Query(1, ge=1, description="Start index (1-based)"),
    count: int | None = Query(None, ge=0, description="Maximum number of results"),
    attributes: str | None = Query(None, description="Comma-separated list of attributes to include"),
    excluded_attributes: str | None = Query(None, description="Comma-separated list of attributes to exclude"),
) -> ListResponse[Group]:
    """
    List groups with optional filtering and pagination.

    Returns a paginated list of groups that match the specified filter.
    """
    logger.debug("REST: List groups", filter=filter, start_index=start_index, count=count)

    try:
        return await group_service.list_groups(filter, start_index, count)
    except Exception as e:
        logger.error("Error listing groups", error=e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) from e


@router.get("/{group_id}", response_model=Group)
@inject
async def get_group(
    group_service: Annotated[GroupService, Depends(Provide[ApplicationContainer.group_service])],
    group_id: str = Path(..., description="Group ID"),
    attributes: str | None = Query(None, description="Comma-separated list of attributes to include"),
    excluded_attributes: str | None = Query(None, description="Comma-separated list of attributes to exclude"),
) -> Group:
    """
    Get a specific group by ID.

    Returns the group with the specified ID.
    """
    logger.debug("REST: Get group with ID", id=group_id)

    try:
        group = await group_service.get_group(group_id)
        return group
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except Exception as e:
        logger.error("Error getting group", id=group_id, error=e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) from e


@router.post("", response_model=Group, status_code=status.HTTP_201_CREATED)
@inject
async def create_group(
    group: Group,
    response: Response,
    group_service: Annotated[GroupService, Depends(Provide[ApplicationContainer.group_service])],
) -> Group:
    """
    Create a new group.

    Creates a group with the provided attributes and returns the created group.
    """
    logger.debug("REST: Create group")

    try:
        created_group = await group_service.create_group(group)
        response.headers["Location"] = f"/Groups/{created_group.id}"
        return created_group
    except MappingError as e:
        logger.error("Error user not found", group_id=e.element, user_id=e.value)
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e)) from e
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e
    except Exception as e:
        logger.error("Error creating group", error=e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) from e


@router.put("/{group_id}", response_model=Group)
@inject
async def update_group(
    group_service: Annotated[GroupService, Depends(Provide[ApplicationContainer.group_service])],
    group_id: str = Path(..., description="Group ID"),
    group: Group = ...,
) -> Group:
    """
    Replace a group.

    Replaces all attributes of the specified group and returns the updated group.
    """
    logger.debug("REST: Update group with ID", id=group_id)

    try:
        return await group_service.update_group(group_id, group)
    except MappingError as e:
        logger.error("Error user not found", group_id=e.element, user_id=e.value)
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e)) from e
    except ValueError as e:
        if "not found" in str(e):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e
    except Exception as e:
        logger.error("Error updating group", id=group_id, error=e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) from e


@router.patch("/{group_id}", response_model=Group)
@inject
async def patch_group(
    group_service: Annotated[GroupService, Depends(Provide[ApplicationContainer.group_service])],
    group_id: Annotated[str, Path(..., description="Group ID")],
    patch_request: Annotated[dict[str, Any], Body(..., description="Raw SCIM-compliant patch request body")],
) -> Group:
    """
    Patch a group using a raw SCIM JSON patch body.
    The request must contain an 'Operations' list, and may optionally contain a 'schemas' field.
    """
    logger.debug("REST: Patch group with ID", id=group_id)

    try:
        operations = patch_request.get("Operations") or patch_request.get("operations")
        if not operations or not isinstance(operations, list):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or missing 'Operations' field in patch body",
            )

        updated_group = await group_service.apply_patch_operations(group_id, operations)
        return updated_group

    except HTTPException as e:
        # Already a well-formed client or not-found error, just raise it
        raise e

    except ValueError as e:
        if "not found" in str(e).lower():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e

    except Exception as e:
        logger.exception("Unexpected error patching group", group_id=group_id)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Unexpected error") from e


@router.delete("/{group_id}", status_code=status.HTTP_204_NO_CONTENT)
@inject
async def delete_group(
    group_service: Annotated[GroupService, Depends(Provide[ApplicationContainer.group_service])],
    group_id: str = Path(..., description="Group ID"),
) -> Response:
    """
    Delete a group.

    Deletes the specified group and returns no content.
    """
    logger.debug("REST: Delete group with ID", id=group_id)

    try:
        success = await group_service.delete_group(group_id)
        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Group {group_id} not found")
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except Exception as e:
        logger.error("Error deleting group", id=group_id, error=e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) from e
