# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH
import operator
from copy import deepcopy
from functools import reduce
from typing import Any

from loguru import logger
from scim2_models import Group, Resource, User


class PatchMixin:
    async def patch_resource(self, resource: Resource, resource_id: str, operations: list[dict[str, Any]]) -> None | User | Group:
        """Apply SCIM patch operations to the resource with the given ID."""

        if isinstance(resource, User):
            cls = User
        elif isinstance(resource, Group):
            cls = Group
        else:
            raise ValueError("Unknown resource type")

        bound_logger = logger.bind(resource_type=cls.__name__, resource_id=resource_id)
        bound_logger.debug("Applying patch operation.")

        resource_data = deepcopy(resource.model_dump())
        # Apply each SCIM operation
        for op in operations:
            path = op["path"]  # e.g., "name.givenName" or "emails"
            op_type = op["op"].lower()

            if not path:
                raise ValueError(f"Operation missing 'path': {op}")

            # Resolve nested keys
            path_parts = path.split(".")

            if op_type == "replace" or op_type == "add":
                value = op["value"]
                try:
                    # Traverse the resource_data dict to reach the parent of the target attribute.
                    # For example, for path "name.givenName", we go to resource_data["name"],
                    # and then set target["givenName"] = value.
                    # If intermediate dicts (like "name") don't exist, we create them.
                    target = resource_data
                    for part in path_parts[:-1]:
                        if part not in target or not isinstance(target[part], dict):
                            target[part] = {}
                        target = target[part]
                    target[path_parts[-1]] = value
                except Exception as e:
                    raise ValueError(f"Failed to apply '{op_type}' on path '{path}': {e}") from e

            elif op_type == "remove":
                try:
                    # Traverse to the parent of the attribute to remove.
                    target = resource_data
                    for part in path_parts[:-1]:
                        if part not in target or not isinstance(target[part], dict):
                            # If parent path doesn't exist, nothing to delete
                            return
                        target = target[part]

                    # Remove the final key if it exists, safely
                    target.pop(path_parts[-1], None)

                except Exception as e:
                    raise ValueError(f"Failed to remove path '{path}': {e}") from e

            else:
                raise ValueError(f"Unsupported patch operation: {op_type}")

        resource_data.pop(
            "meta", None
        )  # Remove problematic meta tag for now TODO think about how we can solve this more elegantly?
        # Rebuild updated Resource model
        updated_resource = cls(**resource_data)
        updated_resource.id = resource_id
        return updated_resource
