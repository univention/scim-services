# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH
from typing import Annotated, Any

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Body, Depends, HTTPException, Path, Query, Response, status
from loguru import logger
from scim2_models import ListResponse

from univention.scim.server.config import application_settings
from univention.scim.server.container import ApplicationContainer
from univention.scim.server.domain.user_service import UserService
from univention.scim.server.models.types import UserWithExtensions
from univention.scim.transformation.exceptions import MappingError


router = APIRouter()


@router.get("", response_model=ListResponse[UserWithExtensions])
@inject
async def list_users(
    user_service: Annotated[UserService, Depends(Provide[ApplicationContainer.user_service])],
    filter: str | None = Query(None, description="SCIM filter expression"),
    start_index: int = Query(1, ge=1, description="Start index (1-based)"),
    count: int | None = Query(None, ge=0, description="Maximum number of results"),
    attributes: str | None = Query(None, description="Comma-separated list of attributes to include"),
    excluded_attributes: str | None = Query(None, description="Comma-separated list of attributes to exclude"),
) -> ListResponse[UserWithExtensions]:
    """
    List users with optional filtering and pagination.

    Returns a paginated list of users that match the specified filter.
    """
    logger.debug("REST: List users with", filter=filter, start_index=start_index, count=count)

    try:
        return await user_service.list_users(filter, start_index, count)
    except Exception as e:
        logger.error("Error listing users", error=e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) from e


@router.get("/{user_id}", response_model=UserWithExtensions)
@inject
async def get_user(
    user_service: Annotated[UserService, Depends(Provide[ApplicationContainer.user_service])],
    user_id: str = Path(..., description="User ID"),
    attributes: str | None = Query(None, description="Comma-separated list of attributes to include"),
    excluded_attributes: str | None = Query(None, description="Comma-separated list of attributes to exclude"),
) -> UserWithExtensions:
    """
    Get a specific user by ID.

    Returns the user with the specified ID.
    """
    logger.debug("REST: Get user with ID", id=user_id)

    try:
        user = await user_service.get_user(user_id)
        return user
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except Exception as e:
        logger.error("Error getting user", id=user_id, error=e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) from e


@router.post("", response_model=UserWithExtensions, status_code=status.HTTP_201_CREATED)
@inject
async def create_user(
    user_service: Annotated[UserService, Depends(Provide[ApplicationContainer.user_service])],
    user: UserWithExtensions,
    response: Response,
) -> UserWithExtensions:
    """
    Create a new user.

    Creates a user with the provided attributes and returns the created user.
    """
    logger.debug("REST: Create user")

    try:
        created_user = await user_service.create_user(user)
        response.headers["Location"] = f"/Users/{created_user.id}"
        return created_user
    except MappingError as e:
        logger.error("Error group not found", user_id=e.element, group_id=e.value)
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e)) from e
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e
    except Exception as e:
        logger.error("Error creating user", error=e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) from e


@router.put("/{user_id}", response_model=UserWithExtensions)
@inject
async def update_user(
    user_service: Annotated[UserService, Depends(Provide[ApplicationContainer.user_service])],
    user_id: str = Path(..., description="User ID"),
    user: UserWithExtensions = ...,
) -> UserWithExtensions:
    """
    Replace a user.

    Replaces all attributes of the specified user and returns the updated user.
    """
    logger.debug("REST: Update user with ID", id=user_id)

    try:
        return await user_service.update_user(user_id, user)
    except MappingError as e:
        logger.error("Error group not found", user_id=e.element, group_id=e.value)
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e)) from e
    except ValueError as e:
        if "not found" in str(e):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e
    except Exception as e:
        logger.error("Error updating user", user_id=user_id, error=e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) from e


@router.patch("/{user_id}", response_model=UserWithExtensions)
@inject
async def patch_user(
    user_service: Annotated[UserService, Depends(Provide[ApplicationContainer.user_service])],
    user_id: Annotated[str, Path(..., description="User ID")],
    patch_request: Annotated[dict[str, Any], Body(..., description="Raw SCIM-compliant patch request body")],
) -> UserWithExtensions:
    """
    Patch a user using a raw SCIM JSON patch body.
    The request must contain an 'Operations' list, and may optionally contain a 'schemas' field.
    """
    settings = application_settings()
    if not settings.patch_enabled:
        raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="PATCH operations are not implemented")

    logger.debug("REST: Patch user with ID", id=user_id)

    try:
        operations = patch_request.get("Operations") or patch_request.get("operations")
        if not operations or not isinstance(operations, list):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or missing 'Operations' field in patch body",
            )

        updated_user = await user_service.apply_patch_operations(user_id, operations)
        return updated_user
    except HTTPException as e:
        # Already a well-formed client or not-found error, just raise it
        raise e
    except MappingError as e:
        logger.error("Error group not found", user_id=e.element, group_id=e.value)
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e)) from e
    except ValueError as e:
        if "not found" in str(e).lower():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e
    except Exception as e:
        logger.exception("Unexpected error patching user", user_id=user_id)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Unexpected error") from e


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
@inject
async def delete_user(
    user_service: Annotated[UserService, Depends(Provide[ApplicationContainer.user_service])],
    user_id: str = Path(..., description="User ID"),
) -> Response:
    """
    Delete a user.

    Deletes the specified user and returns no content.
    """
    logger.debug("REST: Delete user with ID", id=user_id)

    try:
        success = await user_service.delete_user(user_id)
        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User {user_id} not found")
        # The great hack! The SCIM client library expects a HTTP 204 NO_CONTENT with content type ... no comment!
        return Response(status_code=status.HTTP_204_NO_CONTENT, media_type="application/scim+json")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except Exception as e:
        logger.error("Error deleting user", id=user_id, error=e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) from e
