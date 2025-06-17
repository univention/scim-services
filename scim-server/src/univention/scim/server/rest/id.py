# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

from typing import Annotated

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from loguru import logger
from scim2_models import ListResponse

from univention.scim.server.container import ApplicationContainer
from univention.scim.server.domain.group_service import GroupService
from univention.scim.server.domain.user_service import UserService
from univention.scim.server.models.types import GroupWithExtensions, UserWithExtensions


router = APIRouter()


@router.get("/", response_model=ListResponse[UserWithExtensions | GroupWithExtensions])
@inject
async def list_users_and_groups(
    user_service: Annotated[UserService, Depends(Provide[ApplicationContainer.user_service])],
    group_service: Annotated[GroupService, Depends(Provide[ApplicationContainer.group_service])],
    filter: str | None = Query(None, description="SCIM filter expression"),
    start_index: int = Query(1, ge=1, description="Start index (1-based)"),
    count: int | None = Query(None, ge=0, description="Maximum number of results"),
    attributes: str | None = Query(None, description="Comma-separated list of attributes to include"),
    excluded_attributes: str | None = Query(None, description="Comma-separated list of attributes to exclude"),
) -> ListResponse[UserWithExtensions | GroupWithExtensions]:
    """
    List users and groups with optional filtering and pagination.

    Returns a paginated list of users that match the specified filter.
    """
    logger.debug("REST: List users and groups with", filter=filter, start_index=start_index, count=count)

    try:
        users = await user_service.list_users(filter, start_index, count)
        groups = await group_service.list_groups(filter, 1, None)

        group_start = start_index - len(users.resources)
        group_start = group_start if group_start > 0 else 1

        group_count = None
        if count is not None:
            group_count = count - len(users.resources)
            group_count = group_count if group_count > 0 else None

        groups.resources = groups.resources[group_start - 1 : group_count]

        return ListResponse[UserWithExtensions | GroupWithExtensions](
            schemas=["urn:ietf:params:scim:api:messages:2.0:ListResponse"],
            total_results=users.total_results + groups.total_results,
            resources=users.resources + groups.resources,
            start_index=1,
            items_per_page=len(users.resources) + len(groups.resources),
        )
    except Exception as e:
        logger.error("Error listing users and groups", error=e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) from e


@router.get("/{id}", response_model=UserWithExtensions | GroupWithExtensions)
@inject
async def get_user_or_group(
    user_service: Annotated[UserService, Depends(Provide[ApplicationContainer.user_service])],
    group_service: Annotated[GroupService, Depends(Provide[ApplicationContainer.group_service])],
    id: str = Path(..., description="Object ID"),
) -> UserWithExtensions | GroupWithExtensions:
    """
    Get a specific object by ID.

    Returns the object with the specified ID.
    """
    logger.debug("REST: Get object with ID", id=id)

    try:
        user = await user_service.get_user(id)
        return user
    except ValueError:
        try:
            group = await group_service.get_group(id)
            return group
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except Exception as e:
        logger.error("Error getting object", id=id, error=e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) from e
