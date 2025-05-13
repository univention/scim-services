# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

from typing import Any

from fastapi import APIRouter
from loguru import logger
from pydantic import BaseModel
from scim2_models import EnterpriseUser, Group, ListResponse, Schema, User


router = APIRouter()


def _map_pydantic_type_to_scim(pydantic_type: str, field_name: str) -> str:
    """Map Pydantic types to SCIM types."""
    type_mapping = {
        "string": "string",
        "integer": "integer",
        "number": "decimal",
        "boolean": "boolean",
        "object": "complex",
        "null": "string",  # Default to string for null
    }
    return type_mapping.get(pydantic_type, "string")


def _get_field_uniqueness(model_name: str, field_name: str) -> str:
    """Determine the uniqueness attribute based on field and model."""
    if model_name == "User" and field_name == "username":  # due to our udm model this field is name username
        return "server"
    elif model_name == "User" and field_name == "externalId" or model_name == "Group" and field_name == "externalId":
        return "global"
    return "none"


def _get_field_mutability(field_name: str) -> str:
    """Determine the mutability attribute based on field name."""
    immutable_fields = {"id", "meta"}
    if field_name in immutable_fields:
        return "readOnly"
    return "readWrite"


def _get_field_returned(field_name: str) -> str:
    """Determine the returned attribute based on field name."""
    never_returned = {"password"}
    if field_name in never_returned:
        return "never"
    request_fields = {"displayName", "members", "roles"}
    if field_name in request_fields:
        return "request"
    return "default"


def _create_schema_from_model(model: type[BaseModel], schema_id: str, name: str, description: str) -> Schema:
    """Create a SCIM Schema from a Pydantic model."""
    schema_raw = model.model_json_schema()
    properties = schema_raw.get("properties", {})
    required_fields = set(schema_raw.get("required", []))
    attributes: list[dict[str, Any]] = []

    for field_name, prop in properties.items():
        is_multi = prop.get("type") == "array"
        # Handle array types
        if is_multi:
            items = prop.get("items", {})
            if isinstance(items, dict):
                scim_type = _map_pydantic_type_to_scim(items.get("type", "string"), field_name)
            else:
                scim_type = "string"  # Default for complex arrays
        else:
            scim_type = _map_pydantic_type_to_scim(prop.get("type", "string"), field_name)

        # Get field description
        field_description = prop.get("description", f"{field_name} attribute")

        # Create attribute definition
        attr = {
            "name": field_name,
            "type": scim_type,
            "multiValued": is_multi,
            "description": field_description,  # Use field_description here, not the schema description
            "required": field_name in required_fields,
            "caseExact": field_name in {"userName", "password", "displayName"},
            "mutability": _get_field_mutability(field_name),
            "returned": _get_field_returned(field_name),
            "uniqueness": _get_field_uniqueness(name, field_name),
        }

        # [rest of function remains the same]

        attributes.append(attr)

    # Use the provided description parameter for the schema, not from a field
    return Schema(
        id=schema_id,
        name=name,
        description=description,  # Use the description parameter directly
        attributes=attributes,
    )


@router.get("", response_model=ListResponse[Schema], response_model_exclude_none=True)
async def get_schemas() -> Any:
    """
    Get the list of schemas supported by the SCIM service.

    Dynamically builds schema descriptions for all supported SCIM resource types
    using the built-in Schema model from scim2_models.
    """
    logger.debug("REST: Get Schemas")

    schemas = []

    # User Schema
    user_schema = _create_schema_from_model(
        User[EnterpriseUser], "urn:ietf:params:scim:schemas:core:2.0:User", "User", "User Account"
    )
    schemas.append(user_schema)

    # Group Schema
    group_schema = _create_schema_from_model(
        Group, "urn:ietf:params:scim:schemas:core:2.0:Group", "Group", "Group Account"
    )
    schemas.append(group_schema)

    # Add Common Attributes Schema
    common_schema = Schema(
        id="urn:ietf:params:scim:schemas:core:2.0:Common",
        name="Common",
        description="Common attributes that may be present on any SCIM resource",
        attributes=[
            {
                "name": "id",
                "type": "string",
                "multiValued": False,
                "description": "Unique identifier for the resource",
                "required": True,
                "caseExact": True,
                "mutability": "readOnly",
                "returned": "always",
                "uniqueness": "server",
            },
            {
                "name": "externalId",
                "type": "string",
                "multiValued": False,
                "description": "Identifier for the resource as defined by the provisioning client",
                "required": False,
                "caseExact": True,
                "mutability": "readWrite",
                "returned": "default",
                "uniqueness": "global",
            },
            {
                "name": "meta",
                "type": "complex",
                "multiValued": False,
                "description": "Metadata about the resource",
                "required": False,
                "mutability": "readOnly",
                "returned": "default",
                "subAttributes": [
                    {
                        "name": "resourceType",
                        "type": "string",
                        "multiValued": False,
                        "description": "The resource type of the resource",
                        "required": False,
                        "caseExact": True,
                        "mutability": "readOnly",
                        "returned": "default",
                    },
                    {
                        "name": "created",
                        "type": "dateTime",
                        "multiValued": False,
                        "description": "The datetime when the resource was created",
                        "required": False,
                        "mutability": "readOnly",
                        "returned": "default",
                    },
                    {
                        "name": "lastModified",
                        "type": "dateTime",
                        "multiValued": False,
                        "description": "The datetime when the resource was last modified",
                        "required": False,
                        "mutability": "readOnly",
                        "returned": "default",
                    },
                    {
                        "name": "location",
                        "type": "string",
                        "multiValued": False,
                        "description": "The URI of the resource",
                        "required": False,
                        "caseExact": True,
                        "mutability": "readOnly",
                        "returned": "default",
                    },
                    {
                        "name": "version",
                        "type": "string",
                        "multiValued": False,
                        "description": "The version of the resource",
                        "required": False,
                        "caseExact": True,
                        "mutability": "readOnly",
                        "returned": "default",
                    },
                ],
            },
            {
                "name": "schemas",
                "type": "string",
                "multiValued": True,
                "description": "The schemas that are included in the resource",
                "required": True,
                "caseExact": True,
                "mutability": "readOnly",
                "returned": "default",
            },
        ],
    )
    schemas.append(common_schema)

    enterprise_schema = Schema(
        id="urn:ietf:params:scim:schemas:extension:enterprise:2.0:User",
        name="EnterpriseUser",
        description="Enterprise User Extension",
        attributes=[
            {
                "name": "employeeNumber",
                "type": "string",
                "multiValued": False,
                "description": "Numeric or alphanumeric identifier assigned to a person",
            },
        ],
    )
    schemas.append(enterprise_schema)

    return ListResponse[Schema](
        total_results=len(schemas),
        items_per_page=len(schemas),
        start_index=1,
        resources=schemas,
    )
