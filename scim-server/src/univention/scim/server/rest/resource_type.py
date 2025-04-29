# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

from fastapi import APIRouter
from loguru import logger
from pydantic import BaseModel, Field

from univention.scim.server.config import application_settings


router = APIRouter()


class SchemaExtension(BaseModel):
    schema_: str = Field(..., alias="schema")  # 👈 rename internally to schema_
    required: bool
    model_config = {
        "populate_by_name": True,
        "extra": "allow",  # Optional: allows ignoring unexpected fields (robustness)
    }


class Meta(BaseModel):
    location: str
    resourceType: str


class ResourceType(BaseModel):
    schemas: list[str] = Field(default=["urn:ietf:params:scim:schemas:core:2.0:ResourceType"])
    id: str
    name: str
    endpoint: str
    description: str
    schema_: str = Field(..., alias="schema")  # 👈 rename internally to schema_
    schemaExtensions: list[SchemaExtension] | None = None
    meta: Meta
    model_config = {
        "populate_by_name": True,
        "extra": "allow",  # Optional: allows ignoring unexpected fields (robustness)
    }


@router.get("", response_model=list[ResourceType])
async def get_resource_types() -> list[ResourceType]:
    """
    Get the list of resource types supported by the SCIM service.

    Returns a list containing User and Group resource types.
    """
    logger.debug("REST: Get ResourceTypes")

    base_url = application_settings().base_url.rstrip("/")

    user_resource_type = ResourceType(
        id="User",
        name="User",
        endpoint="/Users",
        description="User Account",
        schema_="urn:ietf:params:scim:schemas:core:2.0:User",
        schemaExtensions=[
            SchemaExtension(schema_="urn:ietf:params:scim:schemas:extension:enterprise:2.0:User", required=True)
        ],
        meta=Meta(location=f"{base_url}/ResourceTypes/User", resourceType="ResourceType"),
    )

    group_resource_type = ResourceType(
        id="Group",
        name="Group",
        endpoint="/Groups",
        description="Group",
        schema_="urn:ietf:params:scim:schemas:core:2.0:Group",
        meta=Meta(location=f"{base_url}/ResourceTypes/Group", resourceType="ResourceType"),
    )

    return [user_resource_type, group_resource_type]
