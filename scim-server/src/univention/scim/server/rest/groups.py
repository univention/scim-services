# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

from fastapi import APIRouter, HTTPException, Path, Query, Response
from loguru import logger
from scim2_models import Group, ListResponse

# Internal imports
from univention.scim.server.container import ApplicationContainer


def get_api_router(container: ApplicationContainer) -> APIRouter:
    router = APIRouter()

    @router.get("", response_model=ListResponse[Group])
    async def list_groups(
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
        logger.debug(f"REST: List groups with filter={filter}, start_index={start_index}, count={count}")

        if not container.group_service():
            raise HTTPException(status_code=500, detail="Group service not configured")

        try:
            return await container.group_service().list_groups(filter, start_index, count)
        except Exception as e:
            logger.error(f"Error listing groups: {e}")
            raise HTTPException(status_code=500, detail=str(e)) from e

    @router.get("/{group_id}", response_model=Group)
    async def get_group(
        group_id: str = Path(..., description="Group ID"),
        attributes: str | None = Query(None, description="Comma-separated list of attributes to include"),
        excluded_attributes: str | None = Query(None, description="Comma-separated list of attributes to exclude"),
    ) -> Group:
        """
        Get a specific group by ID.

        Returns the group with the specified ID.
        """
        logger.debug(f"REST: Get group with ID {group_id}")

        if not container.group_service():
            raise HTTPException(status_code=500, detail="Group service not configured")

        try:
            group = await container.group_service().get_group(group_id)
            return group
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e)) from e
        except Exception as e:
            logger.error(f"Error getting group {group_id}: {e}")
            raise HTTPException(status_code=500, detail=str(e)) from e

    @router.post("", response_model=Group, status_code=201)
    async def create_group(group: Group, response: Response) -> Group:
        """
        Create a new group.

        Creates a group with the provided attributes and returns the created group.
        """
        logger.debug("REST: Create group")

        if not container.group_service():
            raise HTTPException(status_code=500, detail="Group service not configured")

        try:
            created_group = await container.group_service().create_group(group)
            response.headers["Location"] = f"/Groups/{created_group.id}"
            return created_group
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e)) from e
        except Exception as e:
            logger.error(f"Error creating group: {e}")
            raise HTTPException(status_code=500, detail=str(e)) from e

    @router.put("/{group_id}", response_model=Group)
    async def update_group(
        group_id: str = Path(..., description="Group ID"),
        group: Group = ...,
    ) -> Group:
        """
        Replace a group.

        Replaces all attributes of the specified group and returns the updated group.
        """
        logger.debug(f"REST: Update group with ID {group_id}")

        if not container.group_service():
            raise HTTPException(status_code=500, detail="Group service not configured")

        try:
            return await container.group_service().update_group(group_id, group)
        except ValueError as e:
            if "not found" in str(e):
                raise HTTPException(status_code=404, detail=str(e)) from e
            raise HTTPException(status_code=400, detail=str(e)) from e
        except Exception as e:
            logger.error(f"Error updating group {group_id}: {e}")
            raise HTTPException(status_code=500, detail=str(e)) from e

    @router.patch("/{group_id}")
    async def patch_group(group_id: str) -> None:
        """
        Patch a group - not implemented yet.

        Updates specified attributes of the group and returns the updated group.
        """
        logger.debug(f"REST: Patch group with ID {group_id}")
        raise HTTPException(status_code=501, detail="PATCH method not implemented")

    @router.delete("/{group_id}", status_code=204)
    async def delete_group(group_id: str = Path(..., description="Group ID")) -> Response:
        """
        Delete a group.

        Deletes the specified group and returns no content.
        """
        logger.debug(f"REST: Delete group with ID {group_id}")

        if not container.group_service():
            raise HTTPException(status_code=500, detail="Group service not configured")

        try:
            success = await container.group_service().delete_group(group_id)
            if not success:
                raise HTTPException(status_code=404, detail=f"Group {group_id} not found")
            return Response(status_code=204)
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e)) from e
        except Exception as e:
            logger.error(f"Error deleting group {group_id}: {e}")
            raise HTTPException(status_code=500, detail=str(e)) from e

    return router
