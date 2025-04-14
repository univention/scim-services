# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH
import re
from typing import Any

from loguru import logger
from scim2_models import Address, Email, Group, Name, PhoneNumber, User, X509Certificate


class UdmToScimMapper:
    """
    Maps UDM objects to SCIM resources.

    Converts UDM properties to SCIM-compatible objects.
    """

    def _convert_ldap_timestamp(self, timestamp: str | None) -> str | None:
        """
        Convert LDAP timestamp format to ISO 8601 format for SCIM.

        Args:
            timestamp: LDAP timestamp string (e.g., "20230101000000Z")

        Returns:
            ISO 8601 formatted timestamp string or None if conversion fails
        """
        if not timestamp:
            return None

        # If already in ISO format (like "2023-01-15T12:30:45Z"), return as is
        if re.match(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$", timestamp):
            return timestamp

        # Match LDAP timestamp pattern: YYYYMMDDHHMMSSZ
        pattern = r"^(\d{4})(\d{2})(\d{2})(\d{2})(\d{2})(\d{2})Z$"
        match = re.match(pattern, timestamp)

        if match:
            # Extract components
            year, month, day, hour, minute, second = match.groups()
            # Format as ISO 8601
            return f"{year}-{month}-{day}T{hour}:{minute}:{second}Z"

        # If timestamp is in another format, log and return as is
        logger.debug(f"Timestamp appears to be in non-standard format: {timestamp}")
        return timestamp

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

        # Get univentionObjectIdentifier for user ID
        user_id = props.get("univentionObjectIdentifier", props.get("username", "unknown"))

        # Get timestamp data from UDM
        udm_created = props.get("createTimestamp")
        udm_modified = props.get("modifyTimestamp")

        # Convert timestamps to ISO 8601 format for SCIM
        created = self._convert_ldap_timestamp(udm_created)
        last_modified = self._convert_ldap_timestamp(udm_modified)

        # Determine resource location
        location = f"{base_url}/Users/{user_id}" if base_url else None

        # Prepare meta object
        meta_data = {
            "resource_type": "User",
            "location": location,
        }

        # Add timestamps if available and converted successfully
        # Ensure timestamps are strings, not datetime objects
        if created:
            meta_data["created"] = created if isinstance(created, str) else created.isoformat().replace("+00:00", "Z")
        if last_modified:
            meta_data["last_modified"] = (
                last_modified if isinstance(last_modified, str) else last_modified.isoformat().replace("+00:00", "Z")
            )

        # Add version if available
        if "HTTP ETag header" in props:
            meta_data["version"] = props["HTTP ETag header"]

        # Set up schemas with core schema only
        schemas = ["urn:ietf:params:scim:schemas:core:2.0:User"]

        # Create User object with basic properties
        user = User(
            schemas=schemas,
            id=user_id,
            user_name=props.get("username", ""),
            active=not props.get("disabled", False),
            meta=meta_data,
            external_id=props.get("univentionObjectIdentifier"),
            display_name=props.get("displayName", ""),
            title=props.get("title"),
            user_type=props.get("employeeType"),
            preferred_language=props.get("preferredLanguage"),
        )

        # Map name
        if "firstname" in props or "lastname" in props or "displayName" in props:
            user.name = Name(
                given_name=props.get("firstname", ""),
                family_name=props.get("lastname", ""),
                formatted=props.get("displayName")
                or f"{props.get('firstname', '')} {props.get('lastname', '')}".strip(),
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
            phone_numbers = props["phone"]
            if isinstance(phone_numbers, str):
                phone_numbers = [phone_numbers]

            for phone in phone_numbers:
                phones.append(PhoneNumber(value=phone, type="work"))

        # UDM "mobile" field is gone, check for mobileTelephoneNumber instead
        if "mobileTelephoneNumber" in props:
            mobile_numbers = props["mobileTelephoneNumber"]
            if isinstance(mobile_numbers, str):
                mobile_numbers = [mobile_numbers]

            for mobile in mobile_numbers:
                phones.append(PhoneNumber(value=mobile, type="mobile"))

        if "homeTelephoneNumber" in props:
            home_numbers = props["homeTelephoneNumber"]
            if isinstance(home_numbers, str):
                home_numbers = [home_numbers]

            for home in home_numbers:
                phones.append(PhoneNumber(value=home, type="home"))

        if "pagerTelephoneNumber" in props:
            pager_numbers = props["pagerTelephoneNumber"]
            if isinstance(pager_numbers, str):
                pager_numbers = [pager_numbers]

            for pager in pager_numbers:
                phones.append(PhoneNumber(value=pager, type="pager"))

        if phones:
            user.phone_numbers = phones

        # Map addresses
        addresses = []
        address_fields = {
            "street": props.get("street"),
            "city": props.get("city"),
            "postcode": props.get("postcode"),
            "country": props.get("country"),
        }

        # If any address field is available, create an address
        if any(address_fields.values()):
            formatted_address = ""
            if address_fields["street"]:
                formatted_address += address_fields["street"] + "\n"
            if address_fields["city"]:
                formatted_address += address_fields["city"] + " "
            if address_fields["postcode"]:
                formatted_address += address_fields["postcode"] + "\n"
            if address_fields["country"]:
                formatted_address += address_fields["country"]

            addresses.append(
                Address(
                    formatted=formatted_address.strip(),
                    street_address=address_fields["street"],
                    locality=address_fields["city"],
                    postal_code=address_fields["postcode"],
                    country=address_fields["country"],
                    type="work",
                )
            )

        if "homePostalAddress" in props:
            # Handle homePostalAddress if it exists (would need proper parsing in real implementation)
            pass

        if addresses:
            user.addresses = addresses

        # Handle X.509 certificates
        certificates = []
        if "userCertificate" in props:
            cert_value = props["userCertificate"]
            display = props.get("certificateSubjectCommonName", "")

            certificates.append(X509Certificate(value=cert_value, display=display))

        if certificates:
            user.x509_certificates = certificates

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

        # Extract group ID from univentionObjectIdentifier
        group_id = props.get("univentionObjectIdentifier", props.get("name", "unknown"))

        # Get timestamp data from UDM
        udm_created = props.get("createTimestamp")
        udm_modified = props.get("modifyTimestamp")

        # Convert timestamps to ISO 8601 format for SCIM
        created = self._convert_ldap_timestamp(udm_created)
        last_modified = self._convert_ldap_timestamp(udm_modified)

        # Prepare meta object
        meta_data = {
            "resource_type": "Group",
            "location": f"{base_url}/Groups/{group_id}" if base_url else None,
        }

        # Add timestamps if available
        if created:
            meta_data["created"] = created
        if last_modified:
            meta_data["last_modified"] = last_modified

        # Add version if available
        if "HTTP ETag header" in props:
            meta_data["version"] = props["HTTP ETag header"]

        # Create Group object
        group = Group(
            schemas=["urn:ietf:params:scim:schemas:core:2.0:Group"],
            id=group_id,
            display_name=props.get("name", ""),
            meta=meta_data,
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
