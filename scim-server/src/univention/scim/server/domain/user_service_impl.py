# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH
from typing import Any, cast
from uuid import uuid4

from loguru import logger
from scim2_models import ListResponse, User

from univention.scim.server.domain.patch_mixin import PatchMixin
from univention.scim.server.domain.repo.crud_manager import CrudManager
from univention.scim.server.domain.rules.evaluate import RuleEvaluator
from univention.scim.server.domain.rules.loader import RuleLoader
from univention.scim.server.domain.user_service import UserService


class UserServiceImpl(UserService, PatchMixin):
    """
    Implementation of the UserService interface.
    Provides domain logic for user management operations.
    """

    def __init__(self, user_repository: CrudManager[User], rule_evaluator: RuleEvaluator | None = None) -> None:
        """
        Initialize the user service.
        Args:
            user_repository: Repository manager for user data
            rule_evaluator: Evaluator for business rules, if None will be loaded from RuleLoader
        """
        self.user_repository = user_repository
        self.rule_evaluator = rule_evaluator or RuleLoader.get_user_rule_evaluator()

    async def get_user(self, user_id: str) -> User:
        """Get a user by ID."""
        logger.debug(f"Getting user with ID: {user_id}")
        user = await self.user_repository.get(user_id)
        if not user:
            raise ValueError(f"User with ID {user_id} not found")
        return user

    async def list_users(
        self, filter_str: str | None = None, start_index: int = 1, count: int | None = None
    ) -> ListResponse[User]:
        """List users with optional filtering and pagination."""
        logger.debug(f"Listing users with filter: {filter_str}, start_index: {start_index}, count: {count}")
        users = await self.user_repository.list(filter_str, start_index, count)
        total = await self.user_repository.count(filter_str)
        return ListResponse[User](
            schemas=["urn:ietf:params:scim:api:messages:2.0:ListResponse"],
            total_results=total,
            resources=users,
            start_index=start_index,
            items_per_page=len(users),
        )

    async def create_user(self, user: User) -> User:
        """Create a new user."""
        logger.debug("Creating new user")
        # Validate user data
        self._validate_user(user)

        # Generate ID if not provided
        if not user.id:
            user.id = str(uuid4())

        # Apply business rules
        user = await self.rule_evaluator.evaluate(user)

        # Create user in repository
        created_user = await self.user_repository.create(user)
        logger.info(f"Created user with ID: {created_user.id}")
        return created_user

    async def update_user(self, user_id: str, user: User) -> User:
        """Update an existing user."""
        logger.debug(f"Updating user with ID: {user_id}")
        # Check if user exists
        existing_user = await self.user_repository.get(user_id)
        if not existing_user:
            raise ValueError(f"User with ID {user_id} not found")

        # Validate user data
        self._validate_user(user)

        # Ensure ID matches
        user.id = user_id

        # Apply business rules
        user = await self.rule_evaluator.evaluate(user)

        # Update user in repository
        updated_user = await self.user_repository.update(user_id, user)
        logger.info(f"Updated user with ID: {user_id}")
        return updated_user

    async def apply_patch_operations(self, user_id: str, operations: list[dict[str, Any]]) -> User:
        """Apply SCIM patch operations to the user with the given ID."""
        logger.debug(f"Applying patch operations to user ID: {user_id}")

        # Fetch the existing user
        existing_user = await self.user_repository.get(user_id)
        if not existing_user:
            raise ValueError(f"User with ID {user_id} not found")

        updated_user: User = cast(User, await self.patch_resource(existing_user, user_id, operations))

        # Validate and apply business rules
        self._validate_user(updated_user)
        updated_resource = await self.rule_evaluator.evaluate(updated_user)

        # Persist the updated user
        saved_user = await self.user_repository.update(user_id, updated_resource)
        logger.info(f"Patched resource with ID: {user_id}")
        return saved_user

    async def delete_user(self, user_id: str) -> bool:
        """Delete a user."""
        logger.debug(f"Deleting user with ID: {user_id}")
        # Check if user exists
        existing_user = await self.user_repository.get(user_id)
        if not existing_user:
            raise ValueError(f"User with ID {user_id} not found")

        # Delete user from repository
        result = await self.user_repository.delete(user_id)
        if result:
            logger.info(f"Deleted user with ID: {user_id}")
        return bool(result)

    def _validate_user(self, user: User) -> None:
        """
        Validate user data.
        Args:
            user: The user to validate
        Raises:
            ValueError: If validation fails
        """
        # Validate required fields
        if not user.user_name:
            raise ValueError("userName is required")
