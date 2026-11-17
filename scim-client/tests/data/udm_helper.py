# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2026 Univention GmbH

import asyncio
import contextlib
import functools as ft
import uuid
from collections.abc import Callable
from typing import Any, Self

from faker import Faker
from faker.providers import address, profile
from lancelog import logger
from univention.admin.rest.client import UDM, Module, Object, ShallowObject

from univention.scim.client.helper import cust_pformat


def generate_udm_users(udm_client: UDM, amount: int, maildomain_name: str) -> list[Any]:
    fake = Faker(["de_DE"])
    fake.add_provider(address)
    fake.add_provider(profile)

    users = []
    for _i in range(0, amount):
        user_name = fake.unique.simple_profile().get("username")
        user_data = {
            "username": user_name,
            "firstname": fake.first_name(),
            "lastname": fake.last_name(),
            "univentionObjectIdentifier": str(uuid.uuid4()),
            "password": "univention",
            "displayName": fake.name(),
            "e-mail": [fake.email()],
            "street": fake.street_address(),
            "postcode": fake.postcode(),
            "city": fake.city(),
            "country": fake.country(),
            "state": fake.state(),
            "phone": [fake.phone_number()],
            "mailPrimaryAddress": f"{user_name}@{maildomain_name}",
            "mailAlternativeAddress": [f"{user_name}.3@{maildomain_name}", f"{user_name}.2@{maildomain_name}"],
        }
        user = create_udm_user(udm_client=udm_client, user_data=user_data)
        users.append(user)

    logger.info("Created {} testusers in UDM.", _i + 1)

    return users


class NoSuchObjectError(Exception):
    """Raised when an object unexpectedly doesn't exist."""


class UDMObjectJanitor:
    """
    Automatic cleanup of UDM objects created for tests.

    Offers CRUD methods for users and groups. All objects created through it
    are deleted on context exit. Methods must be called from an active context
    or an exception is raised. Can be used as either sync or async context
    manager.

    If any objects vanish by other means while the context is active, a
    message is logged but no exception is raised.
    """

    def __init__(self, udm_client: UDM) -> None:
        self._udm_client = udm_client
        self._entered = False
        self._object_deleters: dict[tuple[str, str], Callable[[], Object | None]] = {}

    def __enter__(self) -> Self:
        if self._entered:
            raise RuntimeError("UDMObjectJanitor is already entered.")
        self._entered = True
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> bool | None:
        self._require_entered()
        cleanup = contextlib.ExitStack()
        for deleter in self._object_deleters.values():
            cleanup.callback(deleter)
        self._object_deleters.clear()
        self._entered = False
        return cleanup.__exit__(exc_type, exc_value, traceback)

    async def __aenter__(self) -> Self:
        return await asyncio.to_thread(self.__enter__)

    async def __aexit__(self, exc_type, exc_value, traceback) -> bool | None:
        return await asyncio.to_thread(self.__exit__, exc_type, exc_value, traceback)

    def _require_entered(self) -> None:
        if not self._entered:
            raise RuntimeError("UDMObjectJanitor must be entered before calling its methods.")

    def _track_created(self, resource_type: str, obj: Object, deleter: Callable[[UDM, dict[str, Any]], Object]) -> None:
        identifier = obj.properties["univentionObjectIdentifier"]
        self._object_deleters[resource_type, identifier] = ft.partial(
            self._safe_delete, deleter, {"univentionObjectIdentifier": identifier}
        )

    def _safe_delete(
        self, deleter: Callable[[UDM, dict[str, Any]], Object], object_data: dict[str, Any]
    ) -> Object | None:
        try:
            return deleter(self._udm_client, object_data)
        except NoSuchObjectError:
            logger.info("Object created by this context manager vanished before exit.", object_data=object_data)
            return None

    def create_udm_user(self, user_data: dict[str, Any]) -> Object:
        self._require_entered()
        user = create_udm_user(self._udm_client, user_data)
        self._track_created("user", user, delete_udm_user)
        return user

    def create_udm_group(self, group_data: dict[str, Any]) -> Object:
        self._require_entered()
        group = create_udm_group(self._udm_client, group_data)
        self._track_created("group", group, delete_udm_group)
        return group

    def update_udm_user(self, user_data: dict[str, Any], position: str | None = None) -> Object:
        self._require_entered()
        return update_udm_user(self._udm_client, user_data, position=position)

    def update_udm_group(self, group_data: dict[str, Any]) -> Object:
        self._require_entered()
        return update_udm_group(self._udm_client, group_data)

    def delete_udm_user(self, user_data: dict[str, Any]) -> Object:
        self._require_entered()
        user = delete_udm_user(self._udm_client, user_data)
        self._object_deleters.pop(("user", user_data["univentionObjectIdentifier"]), None)
        return user

    def delete_udm_group(self, group_data: dict[str, Any]) -> Object:
        self._require_entered()
        group = delete_udm_group(self._udm_client, group_data)
        self._object_deleters.pop(("group", group_data["univentionObjectIdentifier"]), None)
        return group


def _get_first_object_matching(module: Module, filter: str) -> Object:
    search = module.search(filter)
    try:
        obj = next(search)
        if isinstance(obj, ShallowObject):
            return obj.open()
        return obj
    except StopIteration as e:
        raise NoSuchObjectError from e


def create_udm_group(udm_client: UDM, group_data: dict[str, Any]) -> Object:
    logger.info("Create udm group")
    logger.debug("udm group data:\n{}", cust_pformat(group_data))

    module = udm_client.get("groups/group")
    logger.debug("udm group module {}", module)
    obj = module.new()
    logger.debug("udm group obj {}", obj)
    for key, value in group_data.items():
        obj.properties[key] = value
    obj.save()

    return obj


def update_udm_group(udm_client: UDM, group_data: dict[str, Any]) -> Object:
    logger.info("Update udm group")
    logger.debug("Group data:\n{}", cust_pformat(group_data))

    module = udm_client.get("groups/group")
    assert module is not None
    obj = _get_first_object_matching(module, f"univentionObjectIdentifier={group_data['univentionObjectIdentifier']}")

    logger.debug("Found group with uoi: {}", group_data["univentionObjectIdentifier"])
    logger.debug("udm group obj {}", obj)

    for key, value in group_data.items():
        obj.properties[key] = value
    obj.save()

    return obj


def delete_udm_group(udm_client: UDM, group_data: dict[str, Any]) -> Object:
    logger.info("Delete udm group")
    logger.debug("Group data:\n{}", cust_pformat(group_data))

    module = udm_client.get("groups/group")
    assert module is not None
    obj = _get_first_object_matching(module, f"univentionObjectIdentifier={group_data['univentionObjectIdentifier']}")

    logger.debug("Found group with uoi: {}", group_data["univentionObjectIdentifier"])

    obj.delete()

    return obj


def create_udm_user(udm_client: UDM, user_data: dict[str, Any]) -> Object:
    logger.info("Create_udm user")
    logger.debug("udm user data:\n{}", cust_pformat(user_data))

    module = udm_client.get("users/user")
    obj = module.new()
    for key, value in user_data.items():
        obj.properties[key] = value
    obj.save()

    return obj


def update_udm_user(udm_client: UDM, user_data: dict[str, Any], position: str | None = None) -> Object:
    logger.info("Update udm user")
    logger.debug("Do update with user data:\n{}", cust_pformat(user_data))

    module = udm_client.get("users/user")
    assert module is not None
    obj = _get_first_object_matching(module, f"univentionObjectIdentifier={user_data['univentionObjectIdentifier']}")

    logger.debug("Found user with uoi in UDM: {}", user_data["univentionObjectIdentifier"])
    logger.debug("Received UDM user date:\n{}", cust_pformat(obj))

    # For move test
    if position:
        obj.position = position

    for key, value in user_data.items():
        obj.properties[key] = value
    obj.save()

    return obj


def delete_udm_user(udm_client: UDM, user_data: dict[str, Any]) -> Object:
    logger.info("Delete udm user")
    logger.debug("udm user data:\n{}", cust_pformat(user_data))

    module = udm_client.get("users/user")
    assert module is not None
    obj = _get_first_object_matching(module, f"univentionObjectIdentifier={user_data['univentionObjectIdentifier']}")

    logger.debug("Found user with uoi: {}", user_data["univentionObjectIdentifier"])

    obj.delete()

    return obj
