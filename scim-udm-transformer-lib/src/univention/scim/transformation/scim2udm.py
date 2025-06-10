# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

from typing import Any

from loguru import logger
from scim2_models import EnterpriseUser, Group, User

from univention.scim.transformation.exceptions import MappingError
from univention.scim.transformation.id_cache import IdCache


class ScimToUdmMapper:
    """
    Maps SCIM resources to UDM properties.

    Converts SCIM objects to the property format expected by UDM.
    """

    def __init__(self, cache: IdCache | None = None):
        """
        Initialize the ScimToUdmMapper.
        Args:
            cache: Cache to map SCIM IDs to DNs
        """
        self.cache = cache

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
            "univentionObjectIdentifier": user.id,
            "preferredLanguage": user.preferred_language,
            "employeeType": user.user_type,
            "title": user.title,
            "displayName": user.display_name,
        }

        for schema, extension in user.get_extension_models().items():
            if not hasattr(user, extension.__name__):
                continue

            extension_obj = getattr(user, extension.__name__)
            if extension_obj is None:
                setattr(user, extension.__name__, extension())
                extension_obj = getattr(user, extension.__name__)

            if schema == EnterpriseUser.to_schema().id:
                logger.debug("Mapping user extension", schema=schema)
                self._map_user_enterprise_extension(extension_obj, properties)
            elif schema == "urn:ietf:params:scim:schemas:extension:Univention:1.0:User":
                logger.debug("Mapping user extension", schema=schema)
                self._map_user_univention_extension(extension_obj, properties)
            elif schema == "urn:ietf:params:scim:schemas:extension:DapUser:2.0:User":
                logger.debug("Mapping user extension", schema=schema)
                self._map_user_customer1_extension(extension_obj, properties)
            else:
                logger.info("Ignoring unknown user extension", schema=schema)

            user.schemas.append(schema)

        if user.roles:
            properties["guardianRoles"] = [x.value for x in user.roles if x.type == "guardian-direct"]

        # Map name components
        if user.name:
            properties["firstname"] = user.name.given_name
            properties["lastname"] = user.name.family_name
        else:
            properties["firstname"] = None
            properties["lastname"] = None

        # Map email addresses
        if user.emails:
            primary_email = next((email.value for email in user.emails if email.type == "mailbox"), None)
            properties["mailPrimaryAddress"] = primary_email
            # Alias emails as alternative addresses
            alias_emails = [email.value for email in user.emails if email.type == "alias"]
            properties["mailAlternativeAddress"] = alias_emails
            # Other emails as e-mails
            other_emails = [email.value for email in user.emails if email.type != "alias" and email.type != "mailbox"]
            properties["e-mail"] = other_emails
        else:
            properties["mailPrimaryAddress"] = None
            properties["mailAlternativeAddress"] = None
            properties["e-mail"] = None

        # Map phone numbers
        if user.phone_numbers:
            work_phone = [phone.value for phone in user.phone_numbers if phone.type == "work"]
            properties["phone"] = work_phone
            mobile_phone = [phone.value for phone in user.phone_numbers if phone.type == "mobile"]
            properties["mobileTelephoneNumber"] = mobile_phone
            pager_phone = [phone.value for phone in user.phone_numbers if phone.type == "pager"]
            properties["pagerTelephoneNumber"] = pager_phone
            home_phone = [phone.value for phone in user.phone_numbers if phone.type == "home"]
            properties["homeTelephoneNumber"] = home_phone
        else:
            properties["phone"] = []
            properties["mobileTelephoneNumber"] = []
            properties["pagerTelephoneNumber"] = []
            properties["homeTelephoneNumber"] = []

        # Map title
        if user.title:
            properties["title"] = user.title

        # TODO: Do not map groups for now, it will reduce performance because many LDAP queries are required
        # Map groups
        # if user.groups and self.cache:
        #    properties["groups"] = []
        #    # UDM expects DNs for members, but SCIM only has IDs
        #    for member in user.groups:
        #        group = self.cache.get_group(member.value)
        #        # When mapping from SCIM to UDM it is a write request to the scim-server
        #        # so we raise an exception if a mapping can not be done
        #        if not group:
        #            raise MappingError(f"Failed to find group {group.dn}", user.id, group.dn)

        #        properties["groups"].append(group.dn)

        # Store any attributes that should be set on the UDM object directly

        # Return both properties and object attributes that should be set on the UDM object directly
        return properties

    def _map_user_enterprise_extension(self, obj: Any, props: dict[str, Any]) -> None:
        props["employeeNumber"] = obj.employee_number

    def _map_user_univention_extension(self, obj: Any, props: dict[str, Any]) -> None:
        props["description"] = obj.description
        props["PasswordRecoveryEmail"] = obj.password_recovery_email

    def _map_user_customer1_extension(self, obj: Any, props: dict[str, Any]) -> None:
        props["primaryOrgUnit"] = obj.primary_org_unit
        props["secondaryOrgUnits"] = obj.secondary_org_units

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
            "univentionObjectIdentifier": group.id,
        }

        for schema, extension in group.get_extension_models().items():
            if not hasattr(group, extension.__name__):
                continue

            extension_obj = getattr(group, extension.__name__)
            if extension_obj is None:
                setattr(group, extension.__name__, extension())
                extension_obj = getattr(group, extension.__name__)

            if schema == "urn:ietf:params:scim:schemas:extension:Univention:1.0:Group":
                logger.debug("Mapping group extension", schema=schema)
                self._map_group_univention_extension(extension_obj, properties)
            else:
                logger.info("Ignoring unknown group extension", schema=schema)

            group.schemas.append(schema)

        # Map members
        if group.members and self.cache:
            members = [x for x in group.members if x.type == "User"]
            nested_groups = [x for x in group.members if x.type == "Group"]

            if len(members) > 0:
                properties["users"] = []
                # UDM expects DNs for members, but SCIM only has IDs
                for member in members:
                    user = self.cache.get_user(member.value)
                    # When mapping from SCIM to UDM it is a write request to the scim-server
                    # so we raise an exception if a mapping can not be done
                    if not user:
                        raise MappingError(f"Failed to find user {member.value}", group.id, member.value)

                    properties["users"].append(user.dn)
            if len(nested_groups) > 0:
                properties["nestedGroup"] = []
                # UDM expects DNs for members, but SCIM only has IDs
                for member in nested_groups:
                    nested_group = self.cache.get_group(member.value)
                    # When mapping from SCIM to UDM it is a write request to the scim-server
                    # so we raise an exception if a mapping can not be done
                    if not nested_group:
                        raise MappingError(f"Failed to find group {member.value}", group.id, member.value)

                    properties["nestedGroup"].append(nested_group.dn)

        # Return both properties and object attributes that should be set on the UDM object directly
        return properties

    def _map_group_univention_extension(self, obj: Any, props: dict[str, Any]) -> None:
        if obj.member_roles:
            props["guardianMemberRoles"] = []

            for member_role in obj.member_roles:
                props["guardianMemberRoles"].append(member_role.value)
