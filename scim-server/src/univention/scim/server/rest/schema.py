from typing import Any, List

from fastapi import APIRouter
from loguru import logger
from scim2_models import User, Schema

router = APIRouter()


@router.get("", response_model=List[Schema])
async def get_schemas() -> Any:
    """
    Get the list of schemas supported by the SCIM service.

    Dynamically builds schema descriptions using the built-in Schema model.
    """
    logger.debug("REST: Get Schemas")

    user_schema_raw = User.model_json_schema()
    properties = user_schema_raw.get("properties", {})
    required_fields = set(user_schema_raw.get("required", []))

    attributes: List[dict] = []

    for name, prop in properties.items():
        is_multi = prop.get("type") == "array"
        # Use the inner type for SCIM when array
        scim_type = (
            prop.get("items", {}).get("type", "string")
            if is_multi else prop.get("type", "string")
        )

        attr = {
            "name": name,
            "type": scim_type,
            "multiValued": is_multi,
            "description": prop.get("description", ""),
            "required": name in required_fields,
            "caseExact": False,
            "mutability": "readWrite",
            "returned": "default",
            "uniqueness": "server" if name == "userName" else "none",
        }
        attributes.append(attr)

    user_schema = Schema(
        id="urn:ietf:params:scim:schemas:core:2.0:User",
        name="User",
        description="User Account",
        attributes=attributes,
    )

    return [user_schema]
