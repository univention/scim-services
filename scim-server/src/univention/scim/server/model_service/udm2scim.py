# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

from typing import Any

from loguru import logger
from scim2_models import Email, Group, Name, PhoneNumber, User


class UdmToScimMapper:
    """
    Maps UDM objects to SCIM resources.

    Converts UDM properties to SCIM-compatible objects.
    """

    def map_user(self, udm_user: dict[str, Any], base_url: str = "") -> User:
        """
        Map UDM user properties to a SCIM User.

        Args:
            udm_user: UDM user object
            base_url: Base URL for resource location

        Returns:
            SCIM User object
        """
        logger.debug(f"Mapping UDM user {udm_user.get('dn')} to SCIM User")

        props = udm_user.get("props", {})

        # Extract user ID from DN
        # This is a simplistic approach; real implementation would need proper ID extraction
        user_id = props.get("username", "unknown")

        # Create User object
        user = User(
            schemas=["urn:ietf:params:scim:schemas:core:2.0:User"],
            id=user_id,
            user_name=props.get("username", ""),
            active=not props.get("disabled", False),
            meta={"resource_type": "User", "location": f"{base_url}/Users/{user_id}" if base_url else None},
        )

        # Map name
        if "firstname" in props or "lastname" in props:
            user.name = Name(
                given_name=props.get("firstname", ""),
                family_name=props.get("lastname", ""),
                formatted=f"{props.get('firstname', '')} {props.get('lastname', '')}".strip(),
            )

        # Map emails
        emails = []
        if "mailPrimaryAddress" in props:
            emails.append(Email(value=props["mailPrimaryAddress"], type="work", primary=True))

        if "mailAlternativeAddress" in props:
            alt_addresses = props["mailAlternativeAddress"]
            if isinstance(alt_addresses, str):
                alt_addresses = [alt_addresses]

            for email in alt_addresses:
                emails.append(Email(value=email, type="other", primary=False))

        if emails:
            user.emails = emails

        # Map phone numbers
        phones = []
        if "phone" in props:
            phones.append(PhoneNumber(value=props["phone"], type="work"))

        if "mobile" in props:
            phones.append(PhoneNumber(value=props["mobile"], type="mobile"))

        if phones:
            user.phone_numbers = phones

        return user

    def map_group(self, udm_group: dict[str, Any], base_url: str = "") -> Group:
        """
        Map UDM group properties to a SCIM Group.

        Args:
            udm_group: UDM group object
            base_url: Base URL for resource location

        Returns:
            SCIM Group object
        """
        logger.debug(f"Mapping UDM group {udm_group.get('dn')} to SCIM Group")

        props = udm_group.get("props", {})

        # Extract group ID from DN
        # This is a simplistic approach; real implementation would need proper ID extraction
        group_id = props.get("name", "unknown")

        # Create Group object
        group = Group(
            schemas=["urn:ietf:params:scim:schemas:core:2.0:Group"],
            id=group_id,
            display_name=props.get("name", ""),
            meta={"resource_type": "Group", "location": f"{base_url}/Groups/{group_id}" if base_url else None},
        )

        # Map members
        # UDM stores member references differently than SCIM expects
        # This is a placeholder implementation
        if "users" in props:
            user_dns = props["users"]
            if isinstance(user_dns, str):
                user_dns = [user_dns]

            # In a real implementation, we would need to convert DNs to SCIM IDs
            # and create proper member references
            group.members = []

        return group
