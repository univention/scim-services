# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

import time
from collections.abc import Callable

import pytest
from scim2_models import Group, GroupMember, User

from helpers.udm_client import MockUdm
from univention.scim.server.domain.repo.udm.udm_id_cache import CacheItem, UdmIdCache


@pytest.fixture
def udm_client(
    random_user_factory: Callable[[list[GroupMember]], User], random_group_factory: Callable[[list[GroupMember]], Group]
) -> MockUdm:
    mock = MockUdm(random_user_factory, random_group_factory)
    mock.add_user()
    mock.add_group()

    return mock


class UdmIdCacheSpy(UdmIdCache):
    def __init__(self, udm_client: MockUdm, ttl: int):
        super().__init__(udm_client, ttl)
        self.call_count = {
            "_get_entry": 0,
            "_query_udm": 0,
            "_query_user": 0,
            "_query_group": 0,
            "get_user": 0,
            "get_group": 0,
        }

    def _get_entry(self, cache: dict[str, CacheItem], key: str) -> CacheItem | None:
        self.call_count["_get_entry"] += 1
        return super()._get_entry(cache, key)

    def _query_udm(self, key: str, udm_module: str) -> CacheItem:
        self.call_count["_query_udm"] += 1
        return super()._query_udm(key, udm_module)

    def _query_user(self, key: str) -> CacheItem:
        self.call_count["_query_user"] += 1
        return super()._query_user(key)

    def _query_group(self, key: str) -> CacheItem:
        self.call_count["_query_group"] += 1
        return super()._query_group(key)

    def get_user(self, key: str) -> CacheItem:
        self.call_count["get_user"] += 1
        return super().get_user(key)

    def get_group(self, key: str) -> CacheItem:
        self.call_count["get_group"] += 1
        return super().get_group(key)


def test_cache_hit_user_dn(udm_client: MockUdm) -> None:
    module = udm_client.get("users/user")
    users = module.search()

    test_user = users[0].open()
    cache = UdmIdCacheSpy(udm_client, 120)

    start = int(time.time())
    cache_item = cache.get_user(test_user.dn)
    assert cache_item.dn == test_user.dn
    assert cache_item.uuid == test_user.properties["univentionObjectIdentifier"]
    assert cache_item.display_name == test_user.properties["displayName"]
    assert cache_item.created >= start
    assert cache_item.created <= int(time.time())

    assert cache.call_count["get_user"] == 1
    assert cache.call_count["_get_entry"] == 1
    # cache is empty so we need to query from UDM
    assert cache.call_count["_query_user"] == 1
    assert cache.call_count["_query_udm"] == 1

    cache_item = cache.get_user(test_user.dn)
    assert cache_item.dn == test_user.dn
    assert cache_item.uuid == test_user.properties["univentionObjectIdentifier"]
    assert cache_item.display_name == test_user.properties["displayName"]
    assert cache_item.created >= start
    assert cache_item.created <= int(time.time())

    assert cache.call_count["get_user"] == 2
    assert cache.call_count["_get_entry"] == 2
    # call count of query still 1 because data is in cache now
    assert cache.call_count["_query_user"] == 1
    assert cache.call_count["_query_udm"] == 1


def test_cache_hit_user_uuid(udm_client: MockUdm) -> None:
    module = udm_client.get("users/user")
    users = module.search()

    test_user = users[0].open()
    cache = UdmIdCacheSpy(udm_client, 120)

    start = int(time.time())
    cache_item = cache.get_user(test_user.properties["univentionObjectIdentifier"])
    assert cache_item.dn == test_user.dn
    assert cache_item.uuid == test_user.properties["univentionObjectIdentifier"]
    assert cache_item.display_name == test_user.properties["displayName"]
    assert cache_item.created >= start
    assert cache_item.created <= int(time.time())

    assert cache.call_count["get_user"] == 1
    assert cache.call_count["_get_entry"] == 1
    # cache is empty so we need to query from UDM
    assert cache.call_count["_query_user"] == 1
    assert cache.call_count["_query_udm"] == 1

    cache_item = cache.get_user(test_user.properties["univentionObjectIdentifier"])
    assert cache_item.dn == test_user.dn
    assert cache_item.uuid == test_user.properties["univentionObjectIdentifier"]
    assert cache_item.display_name == test_user.properties["displayName"]
    assert cache_item.created >= start
    assert cache_item.created <= int(time.time())

    assert cache.call_count["get_user"] == 2
    assert cache.call_count["_get_entry"] == 2
    # call count of query still 1 because data is in cache now
    assert cache.call_count["_query_user"] == 1
    assert cache.call_count["_query_udm"] == 1


def test_cache_hit_group_dn(udm_client: MockUdm) -> None:
    module = udm_client.get("groups/group")
    groups = module.search()

    test_group = groups[0].open()
    cache = UdmIdCacheSpy(udm_client, 120)

    start = int(time.time())
    cache_item = cache.get_group(test_group.dn)
    assert cache_item.dn == test_group.dn
    assert cache_item.uuid == test_group.properties["univentionObjectIdentifier"]
    assert cache_item.display_name == test_group.properties["name"]
    assert cache_item.created >= start
    assert cache_item.created <= int(time.time())

    assert cache.call_count["get_group"] == 1
    assert cache.call_count["_get_entry"] == 1
    # cache is empty so we need to query from UDM
    assert cache.call_count["_query_group"] == 1
    assert cache.call_count["_query_udm"] == 1

    cache_item = cache.get_group(test_group.dn)
    assert cache_item.dn == test_group.dn
    assert cache_item.uuid == test_group.properties["univentionObjectIdentifier"]
    assert cache_item.display_name == test_group.properties["name"]
    assert cache_item.created >= start
    assert cache_item.created <= int(time.time())

    assert cache.call_count["get_group"] == 2
    assert cache.call_count["_get_entry"] == 2
    # call count of query still 1 because data is in cache now
    assert cache.call_count["_query_group"] == 1
    assert cache.call_count["_query_udm"] == 1


def test_cache_hit_group_uuid(udm_client: MockUdm) -> None:
    module = udm_client.get("groups/group")
    groups = module.search()

    test_group = groups[0].open()
    cache = UdmIdCacheSpy(udm_client, 120)

    start = int(time.time())
    cache_item = cache.get_group(test_group.properties["univentionObjectIdentifier"])
    assert cache_item.dn == test_group.dn
    assert cache_item.uuid == test_group.properties["univentionObjectIdentifier"]
    assert cache_item.display_name == test_group.properties["name"]
    assert cache_item.created >= start
    assert cache_item.created <= int(time.time())

    assert cache.call_count["get_group"] == 1
    assert cache.call_count["_get_entry"] == 1
    # cache is empty so we need to query from UDM
    assert cache.call_count["_query_group"] == 1
    assert cache.call_count["_query_udm"] == 1

    cache_item = cache.get_group(test_group.properties["univentionObjectIdentifier"])
    assert cache_item.dn == test_group.dn
    assert cache_item.uuid == test_group.properties["univentionObjectIdentifier"]
    assert cache_item.display_name == test_group.properties["name"]
    assert cache_item.created >= start
    assert cache_item.created <= int(time.time())

    assert cache.call_count["get_group"] == 2
    assert cache.call_count["_get_entry"] == 2
    # call count of query still 1 because data is in cache now
    assert cache.call_count["_query_group"] == 1
    assert cache.call_count["_query_udm"] == 1


def test_cache_query_after_ttl(udm_client: MockUdm) -> None:
    module = udm_client.get("users/user")
    users = module.search()

    test_user = users[0].open()
    cache = UdmIdCacheSpy(udm_client, 1)

    start = int(time.time())
    cache_item = cache.get_user(test_user.dn)
    assert cache_item.dn == test_user.dn
    assert cache_item.uuid == test_user.properties["univentionObjectIdentifier"]
    assert cache_item.display_name == test_user.properties["displayName"]
    assert cache_item.created >= start
    assert cache_item.created <= int(time.time())

    assert cache.call_count["get_user"] == 1
    assert cache.call_count["_get_entry"] == 1
    # cache is empty so we need to query from UDM
    assert cache.call_count["_query_user"] == 1
    assert cache.call_count["_query_udm"] == 1

    cache_item = cache.get_user(test_user.dn)
    assert cache_item.dn == test_user.dn
    assert cache_item.uuid == test_user.properties["univentionObjectIdentifier"]
    assert cache_item.display_name == test_user.properties["displayName"]
    assert cache_item.created >= start
    assert cache_item.created <= int(time.time())

    assert cache.call_count["get_user"] == 2
    assert cache.call_count["_get_entry"] == 2
    # call count of query still 1 because data is in cache now
    assert cache.call_count["_query_user"] == 1
    assert cache.call_count["_query_udm"] == 1

    time.sleep(2)

    start2 = int(time.time())
    cache_item = cache.get_user(test_user.dn)
    assert cache_item.dn == test_user.dn
    assert cache_item.uuid == test_user.properties["univentionObjectIdentifier"]
    assert cache_item.display_name == test_user.properties["displayName"]
    assert cache_item.created >= start2
    assert cache_item.created <= int(time.time())

    assert cache.call_count["get_user"] == 3
    assert cache.call_count["_get_entry"] == 3
    # call count of query is two now because ttl is epxired after 2s
    assert cache.call_count["_query_user"] == 2
    assert cache.call_count["_query_udm"] == 2
