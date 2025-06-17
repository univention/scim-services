# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

import os

from ldap3 import AUTO_BIND_NO_TLS, BASE, SAFE_SYNC, Connection, Server
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
        """ """
        self.scim_client = scim_client

        # TODO Dirty hack - has to be refactored after ProvisioningMessage upgrade
        self.ldap_client = self._ldap3_connect(
            os.environ["LDAP_URL"], os.environ["LDAP_USERNAME"], os.environ["LDAP_PASSWORD"], os.environ["LDAP_BASE_DN"]
        )

        self.ldap_base_dn = os.environ["LDAP_BASE_DN"]

    def _ldap3_connect(self, ldap_uri: str, ldap_admin_user: str, ldap_admin_password: str, ldap_base_dn: str):
        logger.debug("Try connect to {} ({}) with {}", ldap_uri, ldap_base_dn, ldap_admin_user)

        server = Server(ldap_uri)
        ldap_connection = Connection(
            server, ldap_admin_user, ldap_admin_password, client_strategy=SAFE_SYNC, auto_bind=AUTO_BIND_NO_TLS
        )

        logger.debug("Connected to {} ({}) with {}", ldap_uri, ldap_base_dn, ldap_admin_user)

        return ldap_connection

    def get_group(self, key: str) -> CacheItem | None:
        """
        Mapping from groups in the user objects and nested groups are out of scope at the moment.
        """
        pass

    def get_user(self, key: str) -> CacheItem | None:
        """ """
        univention_object_identifier = self.get_univention_object_identifier_by_dn(dn=key)
        if not univention_object_identifier:
            return None

        try:
            scim_user = self.scim_client.get_resource_by_external_id(univention_object_identifier)
            logger.debug("SCIM user:\n{}", cust_pformat(scim_user))

        except ScimClientNoDataFoundException:
            logger.warning(
                "SCIM user with univentionObjectIdentifier {} not found.",
                univention_object_identifier,
            )
            return None

        cache_item = CacheItem(
            dn=key,
            uuid=scim_user.id,
            display_name=scim_user.display_name,
            univention_object_identifier=univention_object_identifier,
        )

        return cache_item

    def get_univention_object_identifier_by_dn(self, dn: str) -> str | None:
        """ """
        logger.debug("Try to get LDAP record for DN {}", dn)

        response = self.ldap_client.extend.standard.paged_search(
            search_base=dn,
            search_filter="(objectClass=univentionObject)",
            search_scope=BASE,
            attributes=["univentionObjectIdentifier"],
            paged_size=1,
        )

        try:
            entry = next(response)
        except StopIteration:
            logger.warning("LDAP user with DN {dn} not found!", dn=dn)
            return None

        univention_object_identifier = entry["attributes"].get("univentionObjectIdentifier")
        logger.debug("LDAP univentionObjectIdentifier: {uoi}", uoi=univention_object_identifier)

        return univention_object_identifier
