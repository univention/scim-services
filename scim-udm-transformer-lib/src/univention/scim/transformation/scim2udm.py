# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

from typing import Any

from loguru import logger
from scim2_models import Group, User


class ScimToUdmMapper:
    """
    Maps SCIM resources to UDM properties.

    Converts SCIM objects to the property format expected by UDM.
    """

    def map_user(self, user: User) -> dict[str, Any]:
        """
        Map a SCIM User to UDM user properties.
        Args:
            user: SCIM User object
        Returns:
            Dictionary of UDM properties and additional UDM object attributes
        """
        logger.debug(f"Mapping SCIM User {user.id} to UDM properties")
        properties = {
            "username": user.user_name,
            "password": user.password,
            "disabled": not user.active if user.active is not None else False,
        }
        if user.id:
            properties["univentionObjectIdentifier"] = user.id
        # Map name components
        if user.name:
            if user.name.given_name:
                properties["firstname"] = user.name.given_name
            if user.name.family_name:
                properties["lastname"] = user.name.family_name
        # Map email addresses
        if user.emails:
            primary_email = next((email.value for email in user.emails if email.primary), None)
            if primary_email:
                properties["mailPrimaryAddress"] = primary_email
            # Additional emails as alternative addresses
            alt_emails = [email.value for email in user.emails if not email.primary]
            if alt_emails:
                properties["mailAlternativeAddress"] = alt_emails
        # Map phone numbers
        if user.phone_numbers:
            work_phone = next((phone.value for phone in user.phone_numbers if phone.type == "work"), None)
            if work_phone:
                properties["phone"] = work_phone
            mobile_phone = next((phone.value for phone in user.phone_numbers if phone.type == "mobile"), None)
            if mobile_phone:
                properties["mobile"] = mobile_phone

        # Store any attributes that should be set on the UDM object directly

        # Map version if available
        if user.meta and user.meta.version:
            properties["etag"] = user.meta.version

        # Return both properties and object attributes that should be set on the UDM object directly
        return properties

    def map_group(self, group: Group) -> dict[str, Any]:
        """
        Map a SCIM Group to UDM group properties.
        Args:
            group: SCIM Group object
        Returns:
            Dictionary of UDM properties and additional UDM object attributes
        """
        logger.debug(f"Mapping SCIM Group {group.id} to UDM properties")
        properties = {
            "name": group.display_name,
            "description": group.display_name,  # Use display name as description if no description is provided
        }
        if group.id:
            properties["univentionObjectIdentifier"] = group.id
        # Map members
        if group.members:
            # UDM expects DNs for members, but SCIM only has IDs
            # This would require a lookup in real implementation
            properties["users"] = [member.value for member in group.members]

        # Map version if available
        if group.meta and group.meta.version:
            properties["etag"] = group.meta.version

        # Return both properties and object attributes that should be set on the UDM object directly
        return properties
