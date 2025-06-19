# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

from ldap3 import AUTO_BIND_NO_TLS, BASE, SAFE_SYNC, Connection, Server
from loguru import logger
from pydantic import AnyUrl
from pydantic_settings import BaseSettings

from univention.scim.consumer.helper import cust_pformat
from univention.scim.consumer.scim_client import ScimClient, ScimClientNoDataFoundException
from univention.scim.transformation.id_cache import CacheItem, IdCache


class LdapSettings(BaseSettings):
    ldap_uri: AnyUrl
    ldap_bind_dn: str
    ldap_bind_password: str


class GroupMembershipLdapResolver(IdCache):
    """ """

    def __new__(cls, *args, **kwargs):
        """
        Singleton
        """
        if not hasattr(cls, "instance"):
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self, scim_client: ScimClient | None = None, ldap_settings: LdapSettings | None = None):
        """ """
        self.scim_client = scim_client

        self.ldap_client = self.connect_to_ldap(ldap_settings or LdapSettings())

    def connect_to_ldap(self, ldap_settings: LdapSettings):
        server = Server(str(ldap_settings.ldap_uri))
        ldap_connection = Connection(
            server,
            ldap_settings.ldap_bind_dn,
            ldap_settings.ldap_bind_password,
            client_strategy=SAFE_SYNC,
            auto_bind=AUTO_BIND_NO_TLS,
        )
        return ldap_connection

    def get_group(self, key: str) -> CacheItem | None:
        """
        Mapping from groups in the user objects and nested groups are out of scope at the moment.
        """
        return None

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

        if (entry := next(response, None)) is None:
            logger.warning("Could not resolve group member DN to SCIM ID. LDAP user with DN {dn} not found!", dn=dn)
            return None

        univention_object_identifier = entry["attributes"].get("univentionObjectIdentifier")
        logger.debug("LDAP univentionObjectIdentifier: {uoi}", uoi=univention_object_identifier)

        return univention_object_identifier
