# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

from collections.abc import Callable
from typing import Any
from unittest.mock import MagicMock

from scim2_models import Group, GroupMember, User
from univention.admin.rest.client import Module, ShallowObject

from univention.scim.transformation import ScimToUdmMapper


class MockUdm:
    def __init__(
        self,
        random_user_factory: Callable[[list[GroupMember]], User],
        random_group_factory: Callable[[list[GroupMember]], Group],
    ):
        self.scim2udm_mapper = ScimToUdmMapper(None)
        self.random_user_factory = random_user_factory
        self.random_group_factory = random_group_factory
        self.users: dict[str, MagicMock] = {}
        self.groups: dict[str, MagicMock] = {}

        user_module = MagicMock(spec=Module)
        user_module.search.side_effect = lambda *args, **kw: self._search(self.users, *args, **kw)
        user_module.get.side_effect = lambda user_id, properties: self.users[user_id].open()
        user_module.new.side_effect = lambda: self._create_object(self.users, self._get_user_dn)

        group_module = MagicMock(spec=Module)
        group_module.search.side_effect = lambda *args, **kw: self._search(self.groups, *args, **kw)
        group_module.get.side_effect = lambda group_id, properties: self.groups[group_id].open()
        group_module.new.side_effect = lambda: self._create_object(self.groups, self._get_group_dn)

        self.modules = {"users/user": user_module, "groups/group": group_module}

    def _get_user_dn(self, obj: MagicMock) -> str:
        return f"cn={obj.properties['username']},ou=user,dc=example,dc=test"

    def _get_group_dn(self, obj: MagicMock) -> str:
        return f"cn={obj.properties['name']},ou=group,dc=example,dc=test"

    def _add_object(self, store: dict[str, MagicMock], obj: MagicMock, get_dn: Callable[[MagicMock], str]) -> None:
        obj_shallow = MagicMock(spec=ShallowObject)
        obj_shallow.open.return_value = obj

        obj.dn = get_dn(obj)
        obj.etag = "1.0"
        print(obj.properties)
        store[obj.dn] = obj_shallow

    def _create_object(self, store: dict[str, MagicMock], get_dn: Callable[[MagicMock], str]) -> MagicMock:
        obj = MagicMock()
        obj.save.side_effect = lambda: self._add_object(store, obj, get_dn)
        obj.delete.side_effect = lambda: store.pop(obj.dn)
        obj.properties = {}

        return obj

    def _search(self, store: dict[str, MagicMock], *args: Any, **kw: Any) -> list[MagicMock]:
        filter = kw.get("filter")
        if not filter:
            return list(store.values())

        key, value = filter.split("=")
        return [obj for obj in store.values() if obj.open().properties[key] == value]

    def get(self, module: str) -> MagicMock:
        return self.modules[module]

    def add_group(self, users: list[str] | None = None) -> MagicMock:
        group_data = self.random_group_factory([])
        group_properties = self.scim2udm_mapper.map_group(group_data)
        if users:
            group_properties["users"] = users

        group = self._create_object(self.groups, self._get_group_dn)
        group.properties = group_properties
        group.save()

        return group

    def add_user(self, groups: list[str] | None = None) -> MagicMock:
        user_data = self.random_user_factory([])
        user_properties = self.scim2udm_mapper.map_user(user_data)
        if groups:
            user_properties["groups"] = groups

        user = self._create_object(self.users, self._get_user_dn)
        user.properties = user_properties
        user.save()

        return user
