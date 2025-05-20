# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

from typing import Any

from loguru import logger
from scim2_models import Address, Email, Group, Name, PhoneNumber, User, X509Certificate

from univention.scim.transformation.id_cache import IdCache


class UdmToScimMapper:
    """
    Maps UDM objects to SCIM resources.

    Converts UDM properties to SCIM-compatible objects.
    """

    def __init__(self, cache: IdCache):
        """
        Initialize the UdmToScimMapper.
        Args:
            cache: Cache to map DNs to SCIM IDs
        """
        self.cache = cache

    def map_user(self, udm_user: Any, base_url: str = "") -> User:
        """
        Map UDM user properties to a SCIM User.
        Args:
            udm_user: UDM user object
            base_url: Base URL for resource location
        Returns:
            SCIM User object
        """
        logger.debug(f"Mapping UDM user {udm_user.dn} to SCIM User")
        # Access properties directly from UDM user object
        props = udm_user.properties
        # Get univentionObjectIdentifier for user ID, fall back to username
        user_id = props.get("univentionObjectIdentifier", props.get("username", "unknown"))

        # Get last_modified timestamp directly from UDM object
        if hasattr(udm_user, "last_modified"):
            pass

        # Determine resource location
        location = f"{base_url}/Users/{user_id}" if base_url else None

        # Prepare meta object
        meta_data = {
            "resource_type": "User",
            "location": location,
        }

        # Add version if available from etag
        if hasattr(udm_user, "etag") and udm_user.etag:
            meta_data["version"] = udm_user.etag

        # Set up schemas with core and enterprise schema
        schemas = [
            "urn:ietf:params:scim:schemas:core:2.0:User",
            # "urn:ietf:params:scim:schemas:extension:enterprise:2.0:User",
        ]

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
        if any(key in props for key in ["firstname", "lastname", "displayName"]):
            user.name = Name(
                given_name=props.get("firstname", ""),
                family_name=props.get("lastname", ""),
                formatted=props.get("displayName")
                or f"{props.get('firstname', '')} {props.get('lastname', '')}".strip(),
            )

        # Map emails
        emails = []
        if "mailPrimaryAddress" in props and props["mailPrimaryAddress"]:
            emails.append(Email(value=props["mailPrimaryAddress"], type="work", primary=True))

        if "mailAlternativeAddress" in props and props["mailAlternativeAddress"]:
            alt_addresses = props["mailAlternativeAddress"]
            if isinstance(alt_addresses, str):
                alt_addresses = [alt_addresses]

            for email in alt_addresses:
                emails.append(Email(value=email, type="other", primary=False))

        if emails:
            user.emails = emails

        # Map phone numbers
        phones = []
        if "phone" in props and props["phone"]:
            phone_numbers = props["phone"]
            if isinstance(phone_numbers, str):
                phone_numbers = [phone_numbers]

            for phone in phone_numbers:
                phones.append(PhoneNumber(value=phone, type="work"))

        if "mobileTelephoneNumber" in props and props["mobileTelephoneNumber"]:
            mobile_numbers = props["mobileTelephoneNumber"]
            if isinstance(mobile_numbers, str):
                mobile_numbers = [mobile_numbers]

            for mobile in mobile_numbers:
                phones.append(PhoneNumber(value=mobile, type="mobile"))

        if "homeTelephoneNumber" in props and props["homeTelephoneNumber"]:
            home_numbers = props["homeTelephoneNumber"]
            if isinstance(home_numbers, str):
                home_numbers = [home_numbers]

            for home in home_numbers:
                phones.append(PhoneNumber(value=home, type="home"))

        if "pagerTelephoneNumber" in props and props["pagerTelephoneNumber"]:
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
            "state": props.get("state"),
        }

        # If any address field is available, create an address
        if any(value for value in address_fields.values() if value):
            formatted_address = ""
            if address_fields["street"]:
                formatted_address += address_fields["street"] + "\n"
            if address_fields["city"]:
                formatted_address += address_fields["city"] + " "
            if address_fields["postcode"]:
                formatted_address += address_fields["postcode"] + "\n"
            if address_fields["state"]:
                formatted_address += address_fields["state"] + " "
            if address_fields["country"]:
                formatted_address += address_fields["country"]

            addresses.append(
                Address(
                    formatted=formatted_address.strip(),
                    street_address=address_fields["street"],
                    locality=address_fields["city"],
                    postal_code=address_fields["postcode"],
                    region=address_fields["state"],
                    country=address_fields["country"],
                    type="work",
                )
            )

        if "homePostalAddress" in props and props["homePostalAddress"]:
            home_addresses = props["homePostalAddress"]
            if isinstance(home_addresses, str):
                home_addresses = [home_addresses]

            if home_addresses:
                # Take first home address and use it
                home_addr = home_addresses[0]
                addresses.append(
                    Address(
                        formatted=home_addr,
                        type="home",
                    )
                )

        if addresses:
            user.addresses = addresses

        # Handle X.509 certificates
        certificates = []
        if hasattr(props, "userCertificate") and props.get("userCertificate"):
            cert_value = props["userCertificate"]
            display = props.get("certificateSubjectCommonName", "")

            certificates.append(X509Certificate(value=cert_value, display=display))

        if certificates:
            user.x509_certificates = certificates

        # Map members if available
        if "groups" in props and props["groups"] and self.cache:
            group_dns = props["groups"]
            if isinstance(group_dns, str):
                group_dns = [group_dns]

            from scim2_models import GroupMember

            for dn in group_dns:
                group = self.cache.get_group(dn)
                if not group:
                    continue

                user.groups.append(
                    GroupMember(
                        value=group,
                        display=group,
                        type="Group",
                    )
                )

        return user

    def map_group(self, udm_group: Any, base_url: str = "") -> Group:
        """
        Map UDM group properties to a SCIM Group.
        Args:
            udm_group: UDM group object
            base_url: Base URL for resource location
        Returns:
            SCIM Group object
        """
        logger.debug(f"Mapping UDM group {udm_group.dn} to SCIM Group")
        # Access properties directly from UDM group object
        props = udm_group.properties
        # Extract group ID
        group_id = props.get("univentionObjectIdentifier", props.get("name", "unknown"))

        # Get last_modified timestamp directly from UDM object
        if hasattr(udm_group, "last_modified"):
            pass

        # Prepare meta object
        meta_data = {
            "resource_type": "Group",
            "location": f"{base_url}/Groups/{group_id}" if base_url else None,
        }

        # Add version if available from etag
        if hasattr(udm_group, "etag") and udm_group.etag:
            meta_data["version"] = udm_group.etag

        # Create Group object
        group = Group(
            schemas=["urn:ietf:params:scim:schemas:core:2.0:Group"],
            id=group_id,
            display_name=props.get("name", ""),
            meta=meta_data,
            external_id=props.get("univentionObjectIdentifier"),
        )

        # Map members if available
        if "users" in props and props["users"] and self.cache:
            user_dns = props["users"]
            if isinstance(user_dns, str):
                user_dns = [user_dns]

            from scim2_models import GroupMember

            for dn in user_dns:
                user = self.cache.get_user(dn)
                if not user:
                    continue

                group.members.append(
                    GroupMember(
                        value=user.uuid,
                        display=user.display_name,
                        type="User",
                    )
                )

        return group
