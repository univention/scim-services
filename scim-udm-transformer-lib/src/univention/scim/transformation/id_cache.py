# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

import time
from abc import ABC, abstractmethod
from uuid import UUID


class CacheItem:
    """
    An item in the cache, holding all required information.
    """

    def __init__(self, dn: str, uuid: UUID, display_name: str):
        """
        Initialize a CacheItem.
        args:
            dn: DN of the object
            uuid: UUID of the object
            display_name: Display name of the object
        """
        self.dn = dn
        self.uuid = uuid
        self.display_name = display_name
        self.created = int(time.time())


class IdCache(ABC):
    """
    Cache to map UDM DNs to SCIM UUIDs
    """

    @abstractmethod
    def get_user(self, key: str) -> CacheItem | None:
        """
        Get a user cache item by DN or UUID

        If item is not yet in the cache it will be fetched from the backend
        args:
            key: Either the dn or the uuid of a cache item
        """
        pass

    @abstractmethod
    def get_group(self, key: str) -> CacheItem | None:
        """
        Get a group cache item by DN or UUID

        If item is not yet in the cache it will be fetched from the backend
        args:
            key: Either the dn or the uuid of a cache item
        """
        pass
