# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH
import operator
from copy import deepcopy
from functools import reduce
from typing import Any

from loguru import logger
from scim2_models import Group, Resource, User


class PatchMixin:
    async def patch_resource(self, resource: Resource, resource_id: str, operations: list[dict[str, Any]]) -> Resource:
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
            value = op["value"]
            op_type = op["op"].lower()

            if not path:
                raise ValueError(f"Operation missing 'path': {op}")

            # Resolve nested keys
            path_parts = path.split(".")

            if op_type == "replace" or op_type == "add":
                try:
                    # Traverse to one level above the target
                    target = reduce(operator.getitem, path_parts[:-1], resource_data)
                    target[path_parts[-1]] = value
                except Exception as e:
                    raise ValueError(f"Failed to apply '{op_type}' on path '{path}': {e}") from e

            elif op_type == "remove":
                try:
                    target = reduce(operator.getitem, path_parts[:-1], resource_data)
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
