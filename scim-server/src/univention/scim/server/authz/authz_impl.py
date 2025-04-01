# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH
from fastapi import HTTPException, Request, status
from loguru import logger
from univention.scim.server.authz.authz import Authorization


class BasicAuthorization(Authorization):
    """
    Implements basic authorization for the SCIM API.

    This is a placeholder implementation for development purposes.
    """

    async def authorize(self, request: Request, user: dict, resource_type: str, operation: str) -> bool:
        """
        Authorize an operation based on user roles.

        Args:
            request: The FastAPI request object
            user: The authenticated user information
            resource_type: The type of resource being accessed
            operation: The operation being performed

        Returns:
            bool: True if the operation is authorized

        Raises:
            HTTPException: If authorization fails
        """
        # Simple role-based authorization
        if "admin" in user.get("roles", []):
            # Admin can do anything
            return True

        # For non-admin users, check specific permissions
        if operation == "read":
            # Everyone can read
            return True

        # Deny other operations
        logger.warning(f"User {user.get('username')} not authorized for {operation} on {resource_type}")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform this operation")
