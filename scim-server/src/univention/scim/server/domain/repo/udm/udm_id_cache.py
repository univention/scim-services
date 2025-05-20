# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

import time
from datetime import UTC, datetime
from uuid import UUID

from loguru import logger
from univention.admin.rest.client import UDM

from univention.scim.transformation.id_cache import CacheItem, IdCache


class UdmIdCache(IdCache):
    """
    IdCache with UDM backend to fetch data from UDM
    """

    def __init__(self, udm_client: UDM, ttl: int):
        """
        Initialize UDMIdCache
        args:
            udm_client: UDM client to use when fetching data
            ttl: Time in seconds after which a cache item will be invalid and refetched
        """
        self.udm_client = udm_client
        self.ttl = ttl
        self.users: dict[str, CacheItem] = {}
        self.groups: dict[str, CacheItem] = {}

    def _get_entry(self, cache: dict[str, CacheItem], key: str) -> CacheItem | None:
        if key not in cache:
            logger.debug("Entry not yet in cache", key=key)
            return None

        logger.debug("Found entry in cache", key=key)

        current_time = int(time.time())
        entry = cache[key]
        if (entry.created + self.ttl) < current_time:
            logger.debug(
                "Cache item expired",
                key=key,
                created=datetime.fromtimestamp(entry.created, tz=UTC),
                current_time=datetime.fromtimestamp(current_time, tz=UTC),
                ttl=self.ttl,
            )
            return None

        return entry

    def _is_uuid(self, val: str) -> bool:
        try:
            UUID(val)
            return True
        except ValueError:
            return False

    def _query_udm(self, key: str, udm_module: str) -> CacheItem:
        module = self.udm_client.get(udm_module)
        properties = ["univentionObjectIdentifier", "displayName", "name"]
        if self._is_uuid(key):
            filter_str = f"univentionObjectIdentifier={key}"
            logger.debug(
                "Fetch item from UDM by univentionObjectIdentifier",
                key=key,
                module=udm_module,
                filter_str=filter_str,
            )

            results = list(module.search(filter_str, properties=properties))
            if not results:
                logger.error("Failed to fetch value from UDM", key=key, module=udm_module, filter_str=filter_str)
                raise ValueError(f"UDM object {udm_module} with {filter_str} not found")

            # Get the first matching object (should be only one)
            udm_obj = results[0].open()
        else:
            logger.debug(
                "Fetch item from UDM by DN",
                key=key,
                module=udm_module,
            )
            udm_obj = module.get(key, properties=properties)
            if not udm_obj:
                logger.error("Failed to fetch value from UDM", key=key, module=udm_module)
                raise ValueError(f"UDM object {udm_module} with {key} not found")

        uuid = None
        if "univentionObjectIdentifier" in udm_obj.properties:
            uuid = udm_obj.properties["univentionObjectIdentifier"]

        item = CacheItem(
            udm_obj.dn,
            uuid,
            udm_obj.properties.get("displayName", udm_obj.properties.get("name", "")),
        )
        logger.debug("Fetched item from UDM", module=udm_module, item=item.__dict__)
        return item

    def _query_user(self, key: str) -> CacheItem:
        user = self._query_udm(key, "users/user")

        self.users[user.dn] = user
        if user.uuid:
            self.users[user.uuid] = user

        return user

    def _query_group(self, key: str) -> CacheItem:
        group = self._query_udm(key, "groups/group")

        self.groups[group.dn] = group
        if group.uuid:
            self.groups[group.uuid] = group

        return group

    def get_user(self, key: str) -> CacheItem | None:
        entry = self._get_entry(self.users, key)
        if not entry:
            entry = self._query_user(key)

        if not entry.uuid:
            logger.error("Ignore user, group member mapping requires a valid 'univentionObjectIdentifier'", user_id=key)
            return None

        return entry

    def get_group(self, key: str) -> CacheItem | None:
        entry = self._get_entry(self.groups, key)
        if not entry:
            entry = self._query_group(key)

        if not entry.uuid:
            logger.error(
                "Ignore group, user groups mapping requires a valid 'univentionObjectIdentifier'", group_id=key
            )
            return None

        return entry
