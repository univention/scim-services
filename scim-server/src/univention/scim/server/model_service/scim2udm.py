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
            Dictionary of UDM properties
        """
        logger.debug(f"Mapping SCIM User {user.id} to UDM properties")

        properties = {
            "username": user.user_name,
            "password": "********",  # Placeholder
            "disabled": not user.active if user.active is not None else False,
        }

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

        return properties

    def map_group(self, group: Group) -> dict[str, Any]:
        """
        Map a SCIM Group to UDM group properties.

        Args:
            group: SCIM Group object

        Returns:
            Dictionary of UDM properties
        """
        logger.debug(f"Mapping SCIM Group {group.id} to UDM properties")

        properties = {
            "name": group.display_name,
            "description": group.display_name,  # Use display name as description if no description is provided
        }

        # Map members
        if group.members:
            # UDM expects DNs for members, but SCIM only has IDs
            # This would require a lookup in real implementation
            properties["users"] = [member.value for member in group.members]

        return properties
