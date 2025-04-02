# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

from fastapi import APIRouter, HTTPException, Path, Query, Response
from loguru import logger
from scim2_models import ListResponse, User

# Internal imports
from univention.scim.server.container import ApplicationContainer


def get_api_router(container: ApplicationContainer) -> APIRouter:
    router = APIRouter()

    @router.get("", response_model=ListResponse[User])
    async def list_users(
        filter: str | None = Query(None, description="SCIM filter expression"),
        start_index: int = Query(1, ge=1, description="Start index (1-based)"),
        count: int | None = Query(None, ge=0, description="Maximum number of results"),
        attributes: str | None = Query(None, description="Comma-separated list of attributes to include"),
        excluded_attributes: str | None = Query(None, description="Comma-separated list of attributes to exclude"),
    ) -> ListResponse[User]:
        """
        List users with optional filtering and pagination.

        Returns a paginated list of users that match the specified filter.
        """
        logger.debug(f"REST: List users with filter={filter}, start_index={start_index}, count={count}")

        if not container.user_service():
            raise HTTPException(status_code=500, detail="User service not configured")

        try:
            return await container.user_service().list_users(filter, start_index, count)
        except Exception as e:
            logger.error(f"Error listing users: {e}")
            raise HTTPException(status_code=500, detail=str(e)) from e

    @router.get("/{user_id}", response_model=User)
    async def get_user(
        user_id: str = Path(..., description="User ID"),
        attributes: str | None = Query(None, description="Comma-separated list of attributes to include"),
        excluded_attributes: str | None = Query(None, description="Comma-separated list of attributes to exclude"),
    ) -> User:
        """
        Get a specific user by ID.

        Returns the user with the specified ID.
        """
        logger.debug(f"REST: Get user with ID {user_id}")

        if not container.user_service():
            raise HTTPException(status_code=500, detail="User service not configured")

        try:
            user = await container.user_service().get_user(user_id)
            return user
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e)) from e
        except Exception as e:
            logger.error(f"Error getting user {user_id}: {e}")
            raise HTTPException(status_code=500, detail=str(e)) from e

    @router.post("", response_model=User, status_code=201)
    async def create_user(user: User, response: Response) -> User:
        """
        Create a new user.

        Creates a user with the provided attributes and returns the created user.
        """
        logger.debug("REST: Create user")

        if not container.user_service():
            raise HTTPException(status_code=500, detail="User service not configured")

        try:
            created_user = await container.user_service().create_user(user)
            response.headers["Location"] = f"/Users/{created_user.id}"
            return created_user
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e)) from e
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            raise HTTPException(status_code=500, detail=str(e)) from e

    @router.put("/{user_id}", response_model=User)
    async def update_user(
        user_id: str = Path(..., description="User ID"),
        user: User = ...,
    ) -> User:
        """
        Replace a user.

        Replaces all attributes of the specified user and returns the updated user.
        """
        logger.debug(f"REST: Update user with ID {user_id}")

        if not container.user_service():
            raise HTTPException(status_code=500, detail="User service not configured")

        try:
            return await container.user_service().update_user(user_id, user)
        except ValueError as e:
            if "not found" in str(e):
                raise HTTPException(status_code=404, detail=str(e)) from e
            raise HTTPException(status_code=400, detail=str(e)) from e
        except Exception as e:
            logger.error(f"Error updating user {user_id}: {e}")
            raise HTTPException(status_code=500, detail=str(e)) from e

    @router.patch("/{user_id}")
    async def patch_user(user_id: str) -> None:
        """
        Patch a user - not implemented yet.

        Updates specified attributes of the user and returns the updated user.
        """
        logger.debug(f"REST: Patch user with ID {user_id}")
        raise HTTPException(status_code=501, detail="PATCH method not implemented")

    @router.delete("/{user_id}", status_code=204)
    async def delete_user(user_id: str = Path(..., description="User ID")) -> Response:
        """
        Delete a user.

        Deletes the specified user and returns no content.
        """
        logger.debug(f"REST: Delete user with ID {user_id}")

        if not container.user_service():
            raise HTTPException(status_code=500, detail="User service not configured")

        try:
            success = await container.user_service().delete_user(user_id)
            if not success:
                raise HTTPException(status_code=404, detail=f"User {user_id} not found")
            return Response(status_code=204)
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e)) from e
        except Exception as e:
            logger.error(f"Error deleting user {user_id}: {e}")
            raise HTTPException(status_code=500, detail=str(e)) from e

    return router
