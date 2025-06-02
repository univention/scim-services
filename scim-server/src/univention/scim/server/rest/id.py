# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

from typing import Annotated

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException, Path, status
from loguru import logger
from scim2_models import Group, User

from univention.scim.server.container import ApplicationContainer
from univention.scim.server.domain.group_service import GroupService
from univention.scim.server.domain.user_service import UserService


router = APIRouter()


@router.get("/{id}", response_model=User | Group)
@inject
async def get_user(
    user_service: Annotated[UserService, Depends(Provide[ApplicationContainer.user_service])],
    group_service: Annotated[GroupService, Depends(Provide[ApplicationContainer.group_service])],
    id: str = Path(..., description="Object ID"),
) -> User:
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
