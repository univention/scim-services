# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

import json
import types
from collections.abc import Callable, Collection, Hashable
from functools import lru_cache
from typing import Any, Generic, TypeVar, Union, cast, get_args, get_origin

from loguru import logger
from scim2_models import EnterpriseUser, Group, Mutability, Resource, User

from univention.scim.transformation.id_cache import IdCache


UserType = TypeVar("UserType", bound=Resource)
GroupType = TypeVar("GroupType", bound=Resource)

_UNIVENTION_USER_EXTENSION_SCHEMA = "urn:ietf:params:scim:schemas:extension:Univention:1.0:User"
_CUSTOMER1_USER_EXTENSION_SCHEMA = "urn:ietf:params:scim:schemas:extension:UniventionUser:2.0:User"
_UNIVENTION_GROUP_EXTENSION_SCHEMA = "urn:ietf:params:scim:schemas:extension:Univention:1.0:Group"


def _normalize_attribute_name(name: str) -> str:
    """Lowercases `name` for case-insensitive attribute-name comparison (RFC 7643 SS2.1)."""
    return name.lower()


def _filter_sub_names(value: dict[str, Any], sub_names: set[str]) -> dict[str, Any]:
    return {
        sub_key: sub_value for sub_key, sub_value in value.items() if _normalize_attribute_name(sub_key) in sub_names
    }


def _filter_by_names(data: dict[str, Any], supported: set[str]) -> dict[str, Any]:
    """Drops keys (and, for dict or list-of-dict values, sub-keys) `supported` does not include."""
    filtered: dict[str, Any] = {}
    for key, value in data.items():
        normalized_key = _normalize_attribute_name(key)
        if normalized_key not in supported:
            continue

        if isinstance(value, dict | list):
            prefix = f"{normalized_key}."
            sub_names = {name[len(prefix) :] for name in supported if name.startswith(prefix)}
            if sub_names:
                if isinstance(value, dict):
                    value = _filter_sub_names(value, sub_names)
                else:
                    value = [_filter_sub_names(item, sub_names) if isinstance(item, dict) else item for item in value]

        filtered[key] = value

    return filtered


def _is_read_only(field: Any) -> bool:
    return Mutability.read_only in field.metadata


def _is_immutable(field: Any) -> bool:
    return Mutability.immutable in field.metadata


def _is_excluded(field: Any, exclude_immutable: bool) -> bool:
    return _is_read_only(field) or (exclude_immutable and _is_immutable(field))


def _is_multi_valued(field: Any) -> bool:
    """Whether `field`'s value is a list rather than a single item, ignoring Optional."""
    annotation = field.annotation
    if get_origin(annotation) in (Union, types.UnionType) and type(None) in get_args(annotation):
        annotation = next(arg for arg in get_args(annotation) if arg is not type(None))
    return get_origin(annotation) is list


@lru_cache(maxsize=64)
def _supported_attribute_names_cached(resource_model: type[Resource], exclude_immutable: bool) -> frozenset[str]:
    names: set[str] = set()
    for field_name, field in resource_model.model_fields.items():
        if not field.serialization_alias or _is_excluded(field, exclude_immutable):
            continue
        names.add(field.serialization_alias)

        sub_model = resource_model.get_field_root_type(field_name)
        if sub_model is not None and hasattr(sub_model, "model_fields"):
            # A multi-valued attribute's sub-attributes are immutable per-entry (RFC 7643
            # SS7): an existing entry's value can't change, but a new entry being added on
            # update has never had one set, so it must still be sendable. Only readOnly is
            # unconditionally excluded there; immutable exclusion only applies to a
            # singular (dict) complex attribute like "name".
            sub_exclude_immutable = exclude_immutable and not _is_multi_valued(field)
            for sub_field in sub_model.model_fields.values():
                if sub_field.serialization_alias and not _is_excluded(sub_field, sub_exclude_immutable):
                    names.add(f"{field.serialization_alias}.{sub_field.serialization_alias}")

    return frozenset(names)


def supported_attribute_names(resource_model: type[Resource], *, exclude_immutable: bool = False) -> frozenset[str]:
    """
    Returns the SCIM attribute names (each field's `serialization_alias`) that
    `resource_model` declares and that are not `Mutability.read_only`. Complex attributes
    also contribute their declared, writable sub-attribute names as
    "attribute.subAttribute" (e.g. "name.formatted").

    `exclude_immutable`: also excludes `Mutability.immutable` attributes. RFC 7643 SS7
    allows an immutable attribute to be set at resource creation but not changed
    afterward.
    """
    return _supported_attribute_names_cached(cast(Hashable, resource_model), exclude_immutable)


class UdmToScimMapper(Generic[UserType, GroupType]):
    """
    Maps UDM objects to SCIM resources.

    Converts UDM properties to SCIM-compatible objects. Builds a plain dict keyed by
    SCIM attribute names/schema URNs and validates it into `user_type`/`group_type`.
    """

    def __init__(
        self,
        cache: IdCache | None = None,
        user_type: type[UserType] = User,
        group_type: type[GroupType] = Group,
        external_id_user_mapping: str | None = None,
        external_id_group_mapping: str | None = None,
        username_mapping: str | None = None,
        roles_user_mapping: str | None = None,
        supported_attributes: Collection[str] | None = None,
    ):
        """
        Initialize the UdmToScimMapper.
        Args:
            cache: Cache to map DNs to SCIM IDs
            user_type: Pydantic model to return when mapping a user
            group_type: Pydantic model to return when mapping a group
            external_id_user_mapping: UDM property to map to SCIM User externalId
            external_id_group_mapping: UDM property to map to SCIM Group externalId
            username_mapping: UDM property to map to SCIM User userName (overrides default 'username')
            roles_user_mapping: UDM property to map to SCIM User roles
            supported_attributes: SCIM attribute names the target server advertises.
              When `None` (default), every mapped attribute is kept.
        """
        self.cache = cache
        self.user_type = user_type
        self.group_type = group_type
        self.external_id_user_mapping = external_id_user_mapping
        self.external_id_group_mapping = external_id_group_mapping
        self.username_mapping = username_mapping
        self.roles_user_mapping = roles_user_mapping
        self.supported_attributes = (
            {_normalize_attribute_name(name) for name in supported_attributes}
            if supported_attributes is not None
            else None
        )

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

    def _filter_supported_attributes(self, data: dict[str, Any]) -> dict[str, Any]:
        if self.supported_attributes is None:
            return data

        return _filter_by_names(data, self.supported_attributes)

    def _filter_extension_attributes(self, data: dict[str, Any], extension_type: type[Resource]) -> dict[str, Any]:
        """Drops keys `extension_type`'s own declared attributes do not include."""
        if self.supported_attributes is None:
            return data

        supported = {_normalize_attribute_name(name) for name in supported_attribute_names(extension_type)}
        return _filter_by_names(data, supported)

    def _get_ref(self, base_url: str, resource_type: str, id: str) -> str | None:
        if not base_url:
            return None

        if resource_type == "Group" or resource_type == "User":
            return f"{base_url}/{resource_type}s/{id}"

        raise ValueError(f"Unknown resource type: {resource_type}")

    def _get_meta(self, base_url: str, obj: Any, resource_type: str) -> dict[str, Any]:
        """
        Map a UDM object to a SCIM "meta" dict.
        Args:
            obj: UDM object
            base_url: Base URL for resource location
        Returns:
            SCIM meta data, keyed by SCIM attribute name
        """
        meta_data: dict[str, Any] = {
            "resourceType": resource_type,
            "location": self._get_ref(base_url, resource_type, obj.properties.get("univentionObjectIdentifier")),
            "created": obj.properties.get("createTimestamp", None),
            "lastModified": obj.properties.get("modifyTimestamp", None),
        }

        # Add version if available from etag
        if hasattr(obj, "etag") and obj.etag:
            meta_data["version"] = obj.etag

        return meta_data

    def _get_formarted_address(self, data: dict[str, str | None]) -> str:
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

    def _map_emails(self, props: dict[str, Any]) -> list[dict[str, Any]] | None:
        emails: list[dict[str, Any]] | None = None
        if "mailPrimaryAddress" in props and props["mailPrimaryAddress"] is not None:
            if not emails:
                emails = []
            emails.append({"value": props["mailPrimaryAddress"], "type": "mailbox", "primary": False})

        if "mailAlternativeAddress" in props and props["mailAlternativeAddress"] is not None:
            if not emails:
                emails = []
            alt_addresses = props["mailAlternativeAddress"]
            if isinstance(alt_addresses, str):
                alt_addresses = [alt_addresses]

            for email in alt_addresses:
                emails.append({"value": email, "type": "alias", "primary": False})

        if "e-mail" in props and props["e-mail"] is not None:
            if not emails:
                emails = []
            for email in props["e-mail"]:
                emails.append({"value": email, "type": "other", "primary": False})

        return emails

    def _map_phone_numbers(self, props: dict[str, Any]) -> list[dict[str, Any]] | None:
        phones: list[dict[str, Any]] | None = None
        if "phone" in props and props["phone"] is not None:
            if not phones:
                phones = []
            for phone in props["phone"]:
                phones.append({"value": phone, "type": "work"})

        if "mobileTelephoneNumber" in props and props["mobileTelephoneNumber"] is not None:
            if not phones:
                phones = []
            for mobile in props["mobileTelephoneNumber"]:
                phones.append({"value": mobile, "type": "mobile"})

        if "homeTelephoneNumber" in props and props["homeTelephoneNumber"] is not None:
            if not phones:
                phones = []
            for home in props["homeTelephoneNumber"]:
                phones.append({"value": home, "type": "home"})

        if "pagerTelephoneNumber" in props and props["pagerTelephoneNumber"] is not None:
            if not phones:
                phones = []
            for pager in props["pagerTelephoneNumber"]:
                phones.append({"value": pager, "type": "pager"})

        return phones

    def _map_addresses(self, props: dict[str, Any]) -> list[dict[str, Any]] | None:
        addresses: list[dict[str, Any]] | None = None
        address_fields: dict[str, str | None] = {
            "street": props.get("street"),
            "city": props.get("city"),
            "postcode": props.get("postcode"),
            "country": props.get("country"),
            "state": props.get("state"),
        }

        # If any address field is available, create an address
        if any(value for value in address_fields.values() if value):
            if not addresses:
                addresses = []
            addresses.append(
                {
                    "formatted": self._get_formarted_address(address_fields),
                    "streetAddress": address_fields["street"],
                    "locality": address_fields["city"],
                    "postalCode": address_fields["postcode"],
                    "region": address_fields["state"],
                    "country": address_fields["country"],
                    "type": "work",
                }
            )

        if "homePostalAddress" in props and props["homePostalAddress"] is not None:
            if not addresses:
                addresses = []
            for address in props["homePostalAddress"]:
                addresses.append(
                    {
                        "formatted": self._get_formarted_address(address),
                        "streetAddress": address.get("street"),
                        "locality": address.get("city"),
                        "postalCode": address.get("zipcode"),
                        "type": "home",
                    }
                )

        return addresses

    def _map_roles(self, props: dict[str, Any]) -> list[dict[str, Any]] | None:
        roles: list[dict[str, Any]] | None = None
        if "guardianRoles" in props and props["guardianRoles"] is not None:
            if not roles:
                roles = []
            for role in props["guardianRoles"]:
                roles.append({"value": role, "type": "guardian-direct"})

        if "guardianInheritedRoles" in props and props["guardianInheritedRoles"] is not None:
            if not roles:
                roles = []
            for role in props["guardianInheritedRoles"]:
                roles.append({"value": role, "type": "guardian-indirect"})

        if self.roles_user_mapping and self.roles_user_mapping in props and props[self.roles_user_mapping] is not None:
            if not roles:
                roles = []

            for role in json.loads(props[self.roles_user_mapping]):
                roles.append(role)

        return roles

    def _map_username(self, props: dict[str, Any]) -> dict[str, Any] | None:
        name_fields = {
            "firstname": props.get("firstname"),
            "lastname": props.get("lastname"),
        }
        if not any(value for value in name_fields.values() if value):
            return None

        formatted = None
        if props.get("firstname"):
            formatted = props.get("firstname")
        if props.get("lastname"):
            if formatted:
                formatted += f" {props.get('lastname')}"
            else:
                formatted = props.get("lastname")

        return {
            "givenName": props.get("firstname"),
            "familyName": props.get("lastname"),
            "formatted": formatted,
        }

    def _map_certificates(self, props: dict[str, Any]) -> list[dict[str, Any]] | None:
        certificates = None
        # FIXME Check how to handle difference between None and [] (Not handled / deleted)
        if props.get("userCertificate"):
            certificates = [{"value": props["userCertificate"], "display": props.get("certificateSubjectCommonName")}]

        return certificates

    def _map_photos(self, props: dict[str, Any]) -> list[dict[str, Any]] | None:
        photos = None
        # UDM's jpegPhoto is base64-encoded and is passed through as-is,
        # just wrapped in a data: URI so it's syntactically a valid URI (Photo.value is a URL
        # reference per RFC 7643) -- some target servers do their own URI-format validation on
        # this value and reject a bare base64 string with a 400.
        if props.get("jpegPhoto"):
            photos = [{"value": f"data:image/jpeg;base64,{props['jpegPhoto']}", "type": "photo"}]

        return photos

    def _user_extension_handlers(
        self, extension_models: dict[str, type[Resource]]
    ) -> dict[str, Callable[[dict[str, Any]], dict[str, Any]]]:
        known: dict[str, Callable[[dict[str, Any]], dict[str, Any]]] = {
            EnterpriseUser.to_schema().id: self._map_user_enterprise_extension,
            _UNIVENTION_USER_EXTENSION_SCHEMA: self._map_user_univention_extension,
            _CUSTOMER1_USER_EXTENSION_SCHEMA: self._map_user_customer1_extension,
        }
        return {schema: handler for schema, handler in known.items() if schema in extension_models}

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
        props = udm_user.properties
        user_id = props.get("univentionObjectIdentifier")

        if not user_id:
            logger.error("univentionObjectIdentifier is required", dn=udm_user.dn)
            raise ValueError("univentionObjectIdentifier is required")

        username_udm_prop = self.username_mapping or "username"
        data: dict[str, Any] = {
            "userName": props.get(username_udm_prop),
            "active": not props.get("disabled", False),
            "displayName": props.get("displayName"),
            "title": props.get("title"),
            "userType": props.get("employeeType"),
            "preferredLanguage": props.get("preferredLanguage"),
            "name": self._map_username(props),
            "emails": self._map_emails(props),
            "phoneNumbers": self._map_phone_numbers(props),
            "addresses": self._map_addresses(props),
            "roles": self._map_roles(props),
            "photos": self._map_photos(props),
            "x509Certificates": self._map_certificates(props),
        }
        data = {key: value for key, value in data.items() if value is not None}
        data = self._filter_supported_attributes(data)

        extension_models = self.user_type.get_extension_models()
        for schema, handler in self._user_extension_handlers(extension_models).items():
            logger.debug("Mapping user extension", schema=schema)
            data[schema] = self._filter_extension_attributes(handler(props), extension_models[schema])

        data["id"] = user_id
        data["meta"] = self._get_meta(base_url, udm_user, "User")

        user = self.user_type.model_validate(data)
        user.external_id = self._get_external_id(udm_user, "User")

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

    def _map_user_enterprise_extension(self, props: dict[str, Any]) -> dict[str, Any]:
        return {"employeeNumber": props.get("employeeNumber")}

    def _map_user_univention_extension(self, props: dict[str, Any]) -> dict[str, Any]:
        return {
            "description": props.get("description"),
            "passwordRecoveryEmail": props.get("PasswordRecoveryEmail"),
        }

    def _map_user_customer1_extension(self, props: dict[str, Any]) -> dict[str, Any]:
        return {
            "primaryOrgUnit": props.get("primaryOrgUnit"),
            "secondaryOrgUnits": props.get("secondaryOrgUnits"),
        }

    def _group_extension_handlers(
        self, extension_models: dict[str, type[Resource]]
    ) -> dict[str, Callable[[dict[str, Any]], dict[str, Any]]]:
        known: dict[str, Callable[[dict[str, Any]], dict[str, Any]]] = {
            _UNIVENTION_GROUP_EXTENSION_SCHEMA: self._map_group_univention_extension,
        }
        return {schema: handler for schema, handler in known.items() if schema in extension_models}

    def _map_group_members(self, props: dict[str, Any], base_url: str) -> list[dict[str, Any]] | None:
        if not self.cache:
            return None

        members: list[dict[str, Any]] | None = None

        if "users" in props and props["users"] is not None:
            if members is None:
                members = []
            for dn in props["users"]:
                cached_user = self.cache.get_user(dn)
                # When mapping from UDM to SCIM it is a read request from the scim-server
                # so just ignore entities which are not found
                if not cached_user:
                    continue
                members.append(
                    {
                        "value": cached_user.uuid,
                        "display": cached_user.display_name,
                        "$ref": self._get_ref(base_url, "User", cached_user.uuid),
                        "type": "User",
                    }
                )

        if "nestedGroup" in props and props["nestedGroup"] is not None:
            if members is None:
                members = []
            for dn in props["nestedGroup"]:
                cached_group = self.cache.get_group(dn)
                if not cached_group:
                    continue
                members.append(
                    {
                        "value": cached_group.uuid,
                        "display": cached_group.display_name,
                        "$ref": self._get_ref(base_url, "Group", cached_group.uuid),
                        "type": "Group",
                    }
                )

        return members

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
        props = udm_group.properties
        group_id = props.get("univentionObjectIdentifier")

        if not group_id:
            logger.error("No univentionObjectIdentifier found", dn=udm_group.dn)
            raise ValueError("univentionObjectIdentifier is required")

        data: dict[str, Any] = {
            "displayName": props.get("name", ""),
            "members": self._map_group_members(props, base_url),
        }
        data = {key: value for key, value in data.items() if value is not None}
        data = self._filter_supported_attributes(data)

        extension_models = self.group_type.get_extension_models()
        for schema, handler in self._group_extension_handlers(extension_models).items():
            logger.debug("Mapping group extension", schema=schema)
            data[schema] = self._filter_extension_attributes(handler(props), extension_models[schema])

        data["id"] = group_id
        data["meta"] = self._get_meta(base_url, udm_group, "Group")

        group = self.group_type.model_validate(data)
        group.external_id = self._get_external_id(udm_group, "Group")

        return cast(GroupType, group)

    def _map_group_univention_extension(self, props: dict[str, Any]) -> dict[str, Any]:
        data: dict[str, Any] = {"description": props.get("description")}
        if props.get("guardianMemberRoles"):
            data["memberRoles"] = [
                {"value": member_role, "type": "guardian"} for member_role in props["guardianMemberRoles"]
            ]
        return data
