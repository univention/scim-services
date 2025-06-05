# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

from typing import Any, Generic, TypeVar, cast

from loguru import logger
from scim2_models import (
    Address,
    Email,
    EnterpriseUser,
    Group,
    GroupMember,
    Meta,
    Name,
    PhoneNumber,
    Resource,
    Role,
    User,
    X509Certificate,
)

from univention.scim.transformation.id_cache import IdCache


UserType = TypeVar("UserType", bound=Resource)
GroupType = TypeVar("GroupType", bound=Resource)


class UdmToScimMapper(Generic[UserType, GroupType]):
    """
    Maps UDM objects to SCIM resources.

    Converts UDM properties to SCIM-compatible objects.
    """

    def __init__(
        self,
        cache: IdCache | None = None,
        user_type: type[UserType] = User,
        group_type: type[GroupType] = Group,
        external_id_user_mapping: str | None = None,
        external_id_group_mapping: str | None = None,
    ):
        """
        Initialize the UdmToScimMapper.
        Args:
            cache: Cache to map DNs to SCIM IDs
            external_id_user_mapping: UDM property to map to SCIM User externalId
            external_id_group_mapping: UDM property to map to SCIM Group externalId
        """
        self.cache = cache
        self.user_type = user_type
        self.group_type = group_type
        self.external_id_user_mapping = external_id_user_mapping
        self.external_id_group_mapping = external_id_group_mapping

    def _get_external_id(self, obj: Any, resource_type: str) -> str | None:
        """
        Get external ID from UDM object based on configuration.

        Args:
            obj: UDM object
            resource_type: Type of resource ("User" or "Group")

        Returns:
            External ID value
        """
        mapping_property = None
        if resource_type == "User":
            mapping_property = self.external_id_user_mapping
        elif resource_type == "Group":
            mapping_property = self.external_id_group_mapping

        # If no mapping configured, use fallback
        if not mapping_property:
            logger.warning("No external ID mapping configured", resource_type=resource_type)
            return None

        # Try to get the configured property
        external_id: str = obj.properties.get(mapping_property)

        if external_id is None:
            logger.warning(
                "Configured external ID property not found in UDM object, external ID will not be mapped",
                resource_type=resource_type,
                configured_property=mapping_property,
                dn=obj.dn,
                available_properties=list(obj.properties.keys()),
            )
            return None

        logger.debug(
            "Mapped external ID from configured property",
            resource_type=resource_type,
            configured_property=mapping_property,
            external_id=external_id,
            dn=obj.dn,
        )
        return external_id

    def _get_ref(self, base_url: str, resource_type: str, id: str) -> str | None:
        if not base_url:
            return None

        if resource_type == "Group" or resource_type == "User":
            return f"{base_url}/{resource_type}s/{id}"

        raise ValueError(f"Unknown resource type: {resource_type}")

    def _get_meta(self, base_url: str, obj: Any, resource_type: str) -> Meta:
        """
        Map UDM object to SCIM Meta object
        Args:
            obj: UDM object
            base_url: Base URL for resource location
        Returns:
            SCIM Meta object
        """
        meta_data = Meta(
            resource_type=resource_type,
            location=self._get_ref(base_url, resource_type, obj.properties.get("univentionObjectIdentifier")),
            created=obj.properties.get("createTimestamp", None),
            last_modified=obj.properties.get("modifyTimestamp", None),
        )

        # Add version if available from etag
        if hasattr(obj, "etag") and obj.etag:
            meta_data.version = obj.etag

        return meta_data

    def _get_formarted_address(self, data: dict[str, str]) -> str:
        formatted_address = ""
        if "street" in data and data["street"]:
            formatted_address += data["street"] + "\n"
        if "city" in data and data["city"]:
            formatted_address += data["city"] + " "
        if "postcode" in data and data["postcode"]:
            formatted_address += data["postcode"] + "\n"
        if "zipcode" in data and data["zipcode"]:
            formatted_address += data["zipcode"] + "\n"
        if "state" in data and data["state"]:
            formatted_address += data["state"] + " "
        if "country" in data and data["country"]:
            formatted_address += data["country"]

        return formatted_address.strip()

    def map_user(self, udm_user: Any, base_url: str = "") -> UserType:
        """
        Map UDM user properties to a SCIM User.
        Args:
            udm_user: UDM user object
            base_url: Base URL for resource location
        Returns:
            SCIM User object
        """
        logger.debug("Mapping UDM user to SCIM User", dn=udm_user.dn)
        # Access properties directly from UDM user object
        props = udm_user.properties
        # Get univentionObjectIdentifier for user ID, fall back to username
        user_id = props.get("univentionObjectIdentifier")

        if not user_id:
            logger.error("univentionObjectIdentifier is required", dn=udm_user.dn)
            raise ValueError("univentionObjectIdentifier is required")

        # Create User object with basic properties
        user = self.user_type(
            id=user_id,
            user_name=props.get("username"),
            active=not props.get("disabled", False),
            meta=self._get_meta(base_url, udm_user, "User"),
            display_name=props.get("displayName"),
            title=props.get("title"),
            user_type=props.get("employeeType"),
            preferred_language=props.get("preferredLanguage"),
        )

        for schema, extension in user.get_extension_models().items():
            if not hasattr(user, extension.__name__):
                continue

            extension_obj = getattr(user, extension.__name__)
            if extension_obj is None:
                setattr(user, extension.__name__, extension())
                extension_obj = getattr(user, extension.__name__)

            if schema == EnterpriseUser.to_schema().id:
                logger.debug("Mapping user extension", schema=schema)
                self._map_user_enterprise_extension(extension_obj, props)
            elif schema == "urn:ietf:params:scim:schemas:extension:Univention:1.0:User":
                logger.debug("Mapping user extension", schema=schema)
                self._map_user_univention_extension(extension_obj, props)
            elif schema == "urn:ietf:params:scim:schemas:extension:DapUser:2.0:User":
                logger.debug("Mapping user extension", schema=schema)
                self._map_user_customer1_extension(extension_obj, props)
            else:
                logger.info("Ignoring unknown user extension", schema=schema)

            user.schemas = user.set_extension_schemas([schema])

        # Map external ID using configurable property
        user.external_id = self._get_external_id(udm_user, "User")

        # Map name
        if any(key in props for key in ["firstname", "lastname"]):
            user.name = Name(
                given_name=props.get("firstname"),
                family_name=props.get("lastname"),
                formatted=f"{props.get('firstname', '')} {props.get('lastname', '')}".strip(),
            )

        # Map emails
        emails = []
        if "mailPrimaryAddress" in props and props["mailPrimaryAddress"]:
            # scim2-models are very strict and only allow specific email types while RFC allows any type
            # so don't use scim2-models email type
            emails.append({"value": props["mailPrimaryAddress"], "type": "mailbox", "primary": True})

        if "mailAlternativeAddress" in props and props["mailAlternativeAddress"]:
            alt_addresses = props["mailAlternativeAddress"]
            if isinstance(alt_addresses, str):
                alt_addresses = [alt_addresses]

            for email in alt_addresses:
                # scim2-models are very strict and only allow specific email types while RFC allows any type
                # so don't use scim2-models email type
                emails.append({"value": email, "type": "alias", "primary": False})

        if "e-mail" in props and props["e-mail"]:
            for email in props["e-mail"]:
                emails.append(Email(value=email, type="other", primary=False))

        if len(emails) > 0:
            user.emails = emails

        # Map phone numbers
        phones = []
        if "phone" in props and props["phone"]:
            phone_numbers = props["phone"]
            for phone in phone_numbers:
                phones.append(PhoneNumber(value=phone, type="work"))

        if "mobileTelephoneNumber" in props and props["mobileTelephoneNumber"]:
            mobile_numbers = props["mobileTelephoneNumber"]
            for mobile in mobile_numbers:
                phones.append(PhoneNumber(value=mobile, type="mobile"))

        if "homeTelephoneNumber" in props and props["homeTelephoneNumber"]:
            home_numbers = props["homeTelephoneNumber"]
            for home in home_numbers:
                phones.append(PhoneNumber(value=home, type="home"))

        if "pagerTelephoneNumber" in props and props["pagerTelephoneNumber"]:
            pager_numbers = props["pagerTelephoneNumber"]
            for pager in pager_numbers:
                phones.append(PhoneNumber(value=pager, type="pager"))

        if len(phones) > 0:
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
            addresses.append(
                Address(
                    formatted=self._get_formarted_address(address_fields),
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

            for address in home_addresses:
                addresses.append(
                    Address(
                        formatted=self._get_formarted_address(address),
                        street_address=address.get("street"),
                        locality=address.get("city"),
                        postal_code=address.get("zipcode"),
                        type="home",
                    )
                )

        if len(addresses) > 0:
            user.addresses = addresses

        # Handle X.509 certificates
        certificates = []
        if props.get("userCertificate"):
            cert_value = props["userCertificate"]
            display = props.get("certificateSubjectCommonName")

            certificates.append(X509Certificate(value=cert_value, display=display))

        if len(certificates) > 0:
            user.x509_certificates = certificates

        # Map roles
        roles = []
        if "guardianRoles" in props and props["guardianRoles"]:
            for role in props["guardianRoles"]:
                roles.append(Role(value=role, type="guardian-direct"))
        if "guardianInheritedRoles" in props and props["guardianInheritedRoles"]:
            for role in props["guardianInheritedRoles"]:
                roles.append(Role(value=role, type="guardian-indirect"))

        if len(roles) > 0:
            user.roles = roles

        # TODO: Do not map groups for now, it will reduce performance because many LDAP queries are required
        # # Map groups if available
        # if "groups" in props and props["groups"] and self.cache:
        #    user.groups = []
        #    group_dns = props["groups"]
        #    if isinstance(group_dns, str):
        #        group_dns = [group_dns]

        #    from scim2_models import GroupMember

        #    for dn in group_dns:
        #        group = self.cache.get_group(dn)
        #        # When mapping from UDM to SCIM it is a read request from the scim-server
        #        # so just ignore entities which are not found
        #        if not group:
        #            continue

        #        user.groups.append(
        #            GroupMember(
        #                value=group,
        #                display=group,
        #                type="Group",
        #            )
        #        )

        return cast(UserType, user)

    def _map_user_enterprise_extension(self, obj: Any, props: dict[str, Any]) -> None:
        obj.employee_number = props.get("employeeNumber")

    def _map_user_univention_extension(self, obj: Any, props: dict[str, Any]) -> None:
        obj.description = props.get("description")
        obj.password_recovery_email = props.get("PasswordRecoveryEmail")

    def _map_user_customer1_extension(self, obj: Any, props: dict[str, Any]) -> None:
        obj.primary_org_unit = props.get("primaryOrgUnit")
        obj.secondary_org_units = props.get("secondaryOrgUnits")

    def map_group(self, udm_group: Any, base_url: str = "") -> GroupType:
        """
        Map UDM group properties to a SCIM Group.
        Args:
            udm_group: UDM group object
            base_url: Base URL for resource location
        Returns:
            SCIM Group object
        """
        logger.debug("Mapping UDM group to SCIM Group", dn=udm_group.dn)
        # Access properties directly from UDM group object
        props = udm_group.properties
        # Extract group ID
        group_id = props.get("univentionObjectIdentifier")

        if not group_id:
            logger.error("No univentionObjectIdentifier found", dn=udm_group.dn)
            raise ValueError("univentionObjectIdentifier is required")

        # Create Group object
        group = self.group_type(
            id=group_id, display_name=props.get("name", ""), meta=self._get_meta(base_url, udm_group, "Group")
        )

        for schema, extension in group.get_extension_models().items():
            if not hasattr(group, extension.__name__):
                continue

            extension_obj = getattr(group, extension.__name__)
            if extension_obj is None:
                setattr(group, extension.__name__, extension())
                extension_obj = getattr(group, extension.__name__)

            if schema == "urn:ietf:params:scim:schemas:extension:Univention:1.0:Group":
                logger.debug("Mapping group extension", schema=schema)
                self._map_group_univention_extension(extension_obj, props)
            else:
                logger.info("Ignoring unknown group extension", schema=schema)

            group.schemas.append(schema)

        # Map external ID using configurable property
        group.external_id = self._get_external_id(udm_group, "Group")

        # Map members if available
        if not group.members:
            group.members = []
        if "users" in props and props["users"] and self.cache:
            user_dns = props["users"]

            for dn in user_dns:
                cached_user = self.cache.get_user(dn)
                # When mapping from UDM to SCIM it is a read request from the scim-server
                # so just ignore entities which are not found
                if not cached_user:
                    continue

                group.members.append(
                    GroupMember(
                        value=cached_user.uuid,
                        display=cached_user.display_name,
                        ref=self._get_ref(base_url, "User", cached_user.uuid),
                        type="User",
                    )
                )

        if "nestedGroup" in props and props["nestedGroup"] and self.cache:
            if not group.members:
                group.members = []

            group_dns = props["nestedGroup"]

            for dn in group_dns:
                cached_group = self.cache.get_group(dn)
                # When mapping from UDM to SCIM it is a read request from the scim-server
                # so just ignore entities which are not found
                if not cached_group:
                    continue

                group.members.append(
                    GroupMember(
                        value=cached_group.uuid,
                        display=cached_group.display_name,
                        ref=self._get_ref(base_url, "Group", cached_group.uuid),
                        type="Group",
                    )
                )

        return cast(GroupType, group)

    def _map_group_univention_extension(self, obj: Any, props: dict[str, Any]) -> None:
        if "guardianMemberRoles" in props and props["guardianMemberRoles"]:
            obj.member_roles = []

            # FIXME: Hack for now to hardcode it, when only using a dict pydantic will fail to serialize it
            from univention.scim.server.models.extensions.univention_group import GuardianMember

            for member_role in props["guardianMemberRoles"]:
                obj.member_roles.append(GuardianMember(value=member_role, type="guardian"))

        obj.description = props.get("description")
