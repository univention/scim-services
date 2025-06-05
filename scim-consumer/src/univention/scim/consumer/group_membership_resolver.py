# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

import os

import ldap
from loguru import logger

from univention.scim.consumer.helper import cust_pformat
from univention.scim.consumer.scim_client import ScimClient, ScimClientNoDataFoundException
from univention.scim.transformation.id_cache import CacheItem, IdCache


class GroupMembershipLdapResolver(IdCache):
    """ """

    def __new__(cls, *args, **kwargs):
        """
        Singleton
        """
        if not hasattr(cls, "instance"):
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self, scim_client: ScimClient | None = None):
        self.scim_client = scim_client
        # TODO Dirty hack - has to be refactored after ProvisioningMessage upgrade
        self.ldap_client = self._ldap_connect(
            os.environ["LDAP_URL"], os.environ["LDAP_USERNAME"], os.environ["LDAP_PASSWORD"], os.environ["LDAP_BASE_DN"]
        )
        self.ldap_base_dn = os.environ["LDAP_BASE_DN"]

    def _ldap_connect(self, ldap_uri: str, ldap_admin_user: str, ldap_admin_password: str, ldap_base_dn: str):
        logger.debug("Try connect to {} ({}) with {}", ldap_uri, ldap_base_dn, ldap_admin_user)

        ldap_connection = ldap.initialize(ldap_uri)
        ldap_connection.simple_bind_s(ldap_admin_user, ldap_admin_password)

        logger.debug("Connected to {} ({}) with {}", ldap_uri, ldap_base_dn, ldap_admin_user)

        return ldap_connection

    def get_group(self, key: str) -> CacheItem | None: ...

    def get_user(self, key: str) -> CacheItem | None:
        """
        Get a user cache item by DN.

        No caching implemented!.
        """
        #
        # Get the univentionObjectIdentifier from LDAP
        #
        univention_object_identifier = self.get_univention_object_identifier_by_dn(dn=key)
        if not univention_object_identifier:
            return None

        #
        # Find user in SCIM by univentionObjectIdentifier
        #
        try:
            scim_user = self.scim_client.get_resource_by_external_id(univention_object_identifier)
            logger.debug("SCIM user:\n{}", cust_pformat(scim_user))

        except ScimClientNoDataFoundException:
            logger.warning(
                "SCIM user with univentionObjectIdentifier {} not found.",
                univention_object_identifier,
            )
            cache_item = None

        else:
            cache_item = CacheItem(
                dn=key,
                uuid=scim_user.id,
                display_name=scim_user.display_name,
                univention_object_identifier=univention_object_identifier,
            )

        return cache_item

    def get_univention_object_identifier_by_dn(self, dn: str) -> str:
        """ """
        logger.debug("Try to get LDAP record for DN {}", dn)
        try:
            result = self.ldap_client.search_s(
                dn,
                ldap.SCOPE_BASE,
                "(objectClass=univentionObject)",
                ["univentionObjectIdentifier"],
            )
        except ldap.NO_SUCH_OBJECT:
            univention_object_identifier = None

        else:
            # Result is a list of tupels. First is the DN, second the entry
            univention_object_identifier = result[0][1].get("univentionObjectIdentifier")
            # FIXME univentionObjectIdentifier is a list?!?!
            univention_object_identifier = univention_object_identifier[0].decode()
            logger.debug("LDAP univentionObjectIdentifier:\n{}", univention_object_identifier)

        if not univention_object_identifier:
            logger.warning("No LDAP record for DN {} found!", dn)
            return None

        else:
            return univention_object_identifier
