# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH
import re
from copy import deepcopy
from typing import Any

from loguru import logger
from scim2_models import Resource

from univention.scim.server.models.types import GroupWithExtensions, UserWithExtensions


class ScimPatchError(Exception):
    """Base exception for SCIM patch errors"""

    def __init__(self, scim_type: str, detail: str, status: int = 400):
        self.scim_type = scim_type
        self.detail = detail
        self.status = status
        super().__init__(detail)


class PathParser:
    """Parse SCIM path expressions"""

    # Regex patterns for parsing SCIM paths
    PATH_PATTERN = re.compile(
        r"^(?P<attribute>[a-zA-Z_]\w*)"
        r"(?:\[(?P<filter>.+?)\])?"
        r"(?:\.(?P<subattr>.+))?$"
    )

    FILTER_PATTERN = re.compile(r'^(?P<attr>\w+)\s+(?P<op>eq|ne|co|sw|ew|gt|ge|lt|le|pr)\s+"?(?P<value>[^"]+)"?$')

    @classmethod
    def parse(cls, path: str) -> dict[str, Any]:
        """Parse a SCIM path into components"""
        if not path:
            return {"schema": None, "attribute": None, "filter": None, "subattr": None}

        schema = None
        # Handle schema-prefixed paths
        if ":" in path:
            schema, path = path.rsplit(":", 1)

        match = cls.PATH_PATTERN.match(path)
        if not match:
            raise ScimPatchError("invalidPath", f"Invalid path: {path}")

        result = match.groupdict()
        result["schema"] = schema

        # Parse filter if present
        if result["filter"]:
            filter_match = cls.FILTER_PATTERN.match(result["filter"])
            if filter_match:
                result["filter"] = filter_match.groupdict()
            else:
                # Simple value filter like [1] for array index
                if result["filter"].isdigit():
                    result["filter"] = {"type": "index", "value": int(result["filter"])}
                else:
                    raise ScimPatchError("invalidFilter", f"Invalid filter: {result['filter']}")

        # Recursively parse subattr if it contains filters
        if result["subattr"] and ("[" in result["subattr"] or "." in result["subattr"]):
            subpath = cls.parse(result["subattr"])
            result["subattr"] = subpath

        return result


class PatchMixin:
    """SCIM-compliant patch implementation"""

    # Attributes that should never be modified
    IMMUTABLE_ATTRS = {"id", "meta.created", "meta.resourceType"}
    READONLY_ATTRS = {"id", "meta", "schemas"}

    async def patch_resource(
        self, resource: Resource, resource_id: str, operations: list[dict[str, Any]]
    ) -> None | UserWithExtensions | GroupWithExtensions:
        """Apply SCIM patch operations to the resource with the given ID."""

        if isinstance(resource, UserWithExtensions):
            cls = UserWithExtensions
        elif isinstance(resource, GroupWithExtensions):
            cls = GroupWithExtensions
        else:
            raise ValueError(f"Unknown resource type: {type(resource)}")

        bound_logger = logger.bind(resource_type=cls.__name__, resource_id=resource_id)
        bound_logger.debug("Applying patch operation.")

        # Deep copy to ensure atomicity
        resource_data = deepcopy(resource.model_dump())
        original_data = deepcopy(resource_data)

        try:
            # Apply each SCIM operation
            for _i, op in enumerate(operations):
                op_type = op.get("op", "").lower()
                path = op.get("path", "")
                value = op.get("value")

                # Validate operation
                if op_type not in ["add", "replace", "remove"]:
                    raise ScimPatchError("invalidSyntax", f"Invalid operation: {op_type}")

                # Remove operations must have a path
                if op_type == "remove" and not path:
                    raise ScimPatchError("noTarget", "Remove operation requires a path")

                # Apply operation
                if op_type == "add":
                    self._apply_add(resource_data, path, value)
                elif op_type == "replace":
                    self._apply_replace(resource_data, path, value)
                elif op_type == "remove":
                    self._apply_remove(resource_data, path)

        except Exception as e:
            # Restore original on any error (atomicity)
            resource_data = original_data
            if isinstance(e, ScimPatchError):
                raise
            raise ScimPatchError("invalidSyntax", str(e)) from e

        # Update meta attributes
        if "meta" not in resource_data:
            resource_data["meta"] = {}

        # Preserve important meta attributes
        if "meta" in original_data:
            resource_data["meta"]["created"] = original_data["meta"].get("created")
            resource_data["meta"]["resourceType"] = original_data["meta"].get("resourceType")

        # Update lastModified
        from datetime import datetime

        resource_data["meta"]["lastModified"] = datetime.utcnow().isoformat() + "Z"

        # Rebuild updated Resource model
        updated_resource = cls(**resource_data)
        updated_resource.id = resource_id
        return updated_resource

    def _apply_add(self, data: Any, path: str, value: Any) -> None:
        """Apply add operation"""
        if not path:
            # No path means add attributes to the resource itself
            if not isinstance(value, dict):
                raise ScimPatchError("invalidValue", "Value must be an object when path is omitted")

            for attr, val in value.items():
                if attr in self.READONLY_ATTRS:
                    continue  # Skip readonly attributes

                if attr in data and isinstance(data[attr], list) and isinstance(val, list):
                    # Merge arrays
                    data[attr].extend(val)
                else:
                    data[attr] = val
            return

        parsed = PathParser.parse(path)
        self._navigate_and_apply(data, parsed, "add", value)

    def _apply_replace(self, data: Any, path: str, value: Any) -> None:
        """Apply replace operation"""
        if not path:
            # No path means replace attributes on the resource itself
            if not isinstance(value, dict):
                raise ScimPatchError("invalidValue", "Value must be an object when path is omitted")

            for attr, val in value.items():
                if attr in self.READONLY_ATTRS:
                    continue
                data[attr] = val
            return

        parsed = PathParser.parse(path)
        self._navigate_and_apply(data, parsed, "replace", value)

    def _apply_remove(self, data: Any, path: str) -> None:
        """Apply remove operation"""
        parsed = PathParser.parse(path)
        self._navigate_and_apply(data, parsed, "remove", None)

    def _navigate_and_apply(self, data: Any, parsed: Any, operation: str, value: Any) -> None:
        """Navigate to the target location and apply the operation"""
        schema = parsed["schema"]
        attribute = parsed["attribute"]
        filter_expr = parsed["filter"]
        subattr = parsed["subattr"]

        # Check if attribute is readonly/immutable
        if attribute in self.READONLY_ATTRS and operation != "add":
            raise ScimPatchError("mutability", f"Cannot modify readonly attribute: {attribute}")

        # Determine the target dictionary
        target_data = data.get(schema) if schema else data

        # Get or create the attribute
        if attribute not in target_data:
            if operation == "remove":
                return  # Nothing to remove
            elif operation in ["add", "replace"]:
                if filter_expr:
                    target_data[attribute] = []  # Create as array if filter present
                elif subattr:
                    target_data[attribute] = {}  # Create as dict if subattr present
                else:
                    target_data[attribute] = None

        current = target_data[attribute]

        # Handle filters on multi-valued attributes
        if filter_expr and isinstance(current, list):
            matching_items = self._apply_filter(current, filter_expr)

            if not matching_items and operation == "replace":
                raise ScimPatchError("noTarget", f"No matching items for filter in attribute: {attribute}")

            if subattr:
                # Apply operation to subattribute of matching items
                for item in matching_items:
                    if isinstance(subattr, dict):
                        self._navigate_and_apply(item, subattr, operation, value)
                    else:
                        self._apply_simple_operation(item, subattr, operation, value)
            else:
                # Apply operation to the matching items themselves
                if operation == "remove":
                    for item in matching_items:
                        current.remove(item)
                elif operation == "replace":
                    # Replace the entire matched item
                    idx = current.index(matching_items[0])
                    current[idx] = value
                elif operation == "add" and not matching_items:
                    # For add with filter, add as new item if no match
                    current.append(value)

        elif filter_expr and not isinstance(current, list):
            # Filter on non-array should fail
            raise ScimPatchError("invalidPath", f"Cannot apply filter to non-array attribute: {attribute}")

        elif subattr:
            # Navigate to subattribute
            if isinstance(subattr, dict):
                self._navigate_and_apply(current, subattr, operation, value)
            else:
                self._apply_simple_operation(current, subattr, operation, value)

        else:
            # Apply to the attribute itself
            if operation == "add":
                if isinstance(current, list):
                    if isinstance(value, list):
                        current.extend(value)
                    else:
                        current.append(value)
                else:
                    target_data[attribute] = value

            elif operation == "replace":
                target_data[attribute] = value

            elif operation == "remove":
                target_data.pop(attribute, None)

    def _apply_filter(self, items: list[Any], filter_expr: Any) -> list[Any]:
        """Apply filter expression to multi-valued attribute"""
        if filter_expr.get("type") == "index":
            idx = filter_expr["value"]
            if 0 <= idx < len(items):
                return [items[idx]]
            return []

        matching = []
        attr = filter_expr.get("attr")
        op = filter_expr.get("op")
        value = filter_expr.get("value")

        for item in items:
            item_value = item.get(attr) if isinstance(item, dict) else None

            if self._evaluate_filter(item_value, op, value):
                matching.append(item)

        return matching

    def _evaluate_filter(self, item_value: Any, op: str, value: Any) -> bool:
        """Evaluate a single filter condition"""
        if op == "eq":
            return str(item_value) == str(value)
        elif op == "ne":
            return str(item_value) != str(value)
        elif op == "co":
            return str(value) in str(item_value)
        elif op == "sw":
            return str(item_value).startswith(str(value))
        elif op == "ew":
            return str(item_value).endswith(str(value))
        elif op == "pr":
            return item_value is not None
        elif op in ["gt", "ge", "lt", "le"]:
            try:
                if op == "gt":
                    return float(item_value) > float(value)
                elif op == "ge":
                    return float(item_value) >= float(value)
                elif op == "lt":
                    return float(item_value) < float(value)
                elif op == "le":
                    return float(item_value) <= float(value)
            except (ValueError, TypeError):
                return False
        return False

    def _apply_simple_operation(self, target: Any, attr: str, operation: str, value: Any) -> None:
        """Apply operation to a simple attribute"""
        if operation == "add" or operation == "replace":
            target[attr] = value
        elif operation == "remove":
            target.pop(attr, None)
