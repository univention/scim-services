# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2026 Univention GmbH

import asyncio
import enum
import os
import time
import uuid
from collections.abc import Awaitable, Callable
from typing import Any, Literal, Protocol

import httpx2
import pytest
from hamcrest import all_of, anything, assert_that, has_properties, instance_of
from hamcrest.core.matcher import Matcher
from lancelog import logger
from scim2_client.engines.httpx2 import SyncSCIMClient
from scim2_models import (
    Email,
    Group,
    ListResponse,
    Role,
    ScimFilter,
    ScimPolicy,
    ScimProvider,
    SearchRequest,
    User,
)
from univention.admin.rest.client import Object

from univention.provisioning.error_handling.db import DBSession
from univention.scim.client.authentication import AuthMethod, BearerAuth, BearerAuthSettings

from ..data.helper import BackgroundConsumer
from ..data.udm_helper import UDMObjectJanitor


def _tests_should_be_run() -> bool:
    conf_str = os.environ.get("TESTCONF_RUN_WIRE_COM_INTEGRATION_TESTS", "true").lower()
    if conf_str not in ["true", "false"]:
        raise ValueError("invalid configuration of TESTCONF_RUN_WIRE_COM_INTEGRATION_TESTS (use true|false)")
    should_be_run = conf_str == "true"
    if not should_be_run and "TESTCONF_WIRE_COM_SCIM_BEARER_TOKEN" in os.environ:
        # If a token is configured the intention is probably to run the tests. Make sure we don't skip them
        # accidentally.
        raise RuntimeError(
            "configuration says wire.com tests should be skipped, but TESTCONF_WIRE_COM_SCIM_BEARER_TOKEN is configured"
        )
    return should_be_run


NUM_TEST_USERS = 1
WIRE_COM_SCIM_SERVER_BASE_URL = "https://prod-nginz-https.wire.com/scim/v2"
ALREADY_EXISTING_USERNAME = "univention_integration_tests"  # This is the username of our test account.


class ValidWireComRoleValues(enum.StrEnum):
    owner = "owner"
    admin = "admin"
    member = "member"
    partner = "partner"


class UserPropertiesFactory(Protocol):
    def __call__(
        self,
        user_index: int,
        *,
        email_attrs: list[Literal["mailPrimaryAddress", "mailAlternativeAddress", "e-mail"]],
        **override_properties: Any,
    ) -> dict[str, Any]: ...


def expected_user_for_udm_user(udm_user: Object, **override_properties) -> Matcher:
    external_id_property_name = os.environ["EXTERNAL_ID_USER_MAPPING"]
    expected_properties = {
        "external_id": udm_user.properties[external_id_property_name],
        "user_name": udm_user.properties["username"],
        "display_name": udm_user.properties["displayName"],
        "preferred_language": udm_user.properties["preferredLanguage"],
        "emails": [Email(value=udm_user.properties["mailPrimaryAddress"], type=Email.Type("mailbox"), primary=False)],
        "roles": [Role(value="member")],
        "active": False,
    }
    expected_properties |= override_properties
    return all_of(instance_of(User), has_properties(**expected_properties))


@pytest.mark.skipif(
    not _tests_should_be_run(), reason="Test has been deconfigured via TESTCONF_RUN_WIRE_COM_INTEGRATION_TESTS=false."
)
@pytest.mark.wire_com_integration_tests
class TestWireComIntegration:
    @pytest.fixture(scope="session")
    def wire_com_scim_bearer_token(self):
        return os.environ["TESTCONF_WIRE_COM_SCIM_BEARER_TOKEN"]

    @pytest.fixture(autouse=True)
    def set_up_env(self, monkeypatch: pytest.MonkeyPatch, wire_com_scim_bearer_token):
        monkeypatch.setenv("GROUP_SYNC_ENABLED", "false")  # Group sync is untested for wire.com.
        monkeypatch.setenv("SCIM_SERVER_BASE_URL", WIRE_COM_SCIM_SERVER_BASE_URL)
        monkeypatch.setenv("SCIM_AUTH_METHOD", AuthMethod.BEARER)
        monkeypatch.setenv("SCIM_BEARER_TOKEN", wire_com_scim_bearer_token)

    @pytest.fixture(scope="session")
    def independent_client(self, wire_com_scim_bearer_token):
        auth = BearerAuth(BearerAuthSettings(scim_bearer_token=wire_com_scim_bearer_token))
        http_client = httpx2.Client(
            auth=auth,
            base_url=WIRE_COM_SCIM_SERVER_BASE_URL,
            headers={
                "Accept": "application/scim+json",
                "Content-Type": "application/scim+json",
            },
        )
        provider = ScimProvider(models=[User, Group], policy=ScimPolicy(unknown=ScimPolicy.Unknown.keep))
        return SyncSCIMClient(client=http_client, provider=provider)

    @pytest.fixture(autouse=True)
    def clean_test_users(self, independent_client: SyncSCIMClient, get_user: Callable[[int], User | None]):
        existing_test_users = [get_user(user_index) for user_index in range(NUM_TEST_USERS)]
        if any(existing_test_users):
            logger.warning(
                "Found existing test users. Is there another test going on right now? We'll wait a while to let it "
                "finish.",
                existing_users=existing_test_users,
            )
            time.sleep(60)
            existing_test_users = [get_user(user_index) for user_index in range(NUM_TEST_USERS)]
            if not any(existing_test_users):
                logger.info("Existing test users vanished, the other test must have finished.")
            else:
                logger.warning(
                    "Existing test users are still there. Assuming they were not cleaned up after a broken test. "
                    "Deleting them now."
                )
                for user in existing_test_users:
                    if user:
                        independent_client.delete(user)
        # Yield to run our tests.
        yield
        # After the test, clean up all test users that still exist at wire.com.
        for user in [get_user(user_index) for user_index in range(NUM_TEST_USERS)]:
            if user:
                logger.info("Deleting user after tests.", user_external_id=user.external_id)
                independent_client.delete(user)

    @pytest.fixture
    def make_wire_com_user_properties(self, maildomain: str) -> UserPropertiesFactory:
        def factory(
            user_index: int,
            *,
            email_attrs: list[Literal["mailPrimaryAddress", "mailAlternativeAddress", "e-mail"]],
            **override_properties: Any,
        ) -> dict[str, Any]:
            assert user_index < NUM_TEST_USERS
            unique_user_name = f"univention-test-user-{user_index}-{uuid.uuid4()}"
            properties: dict[str, Any] = {
                "univentionObjectIdentifier": str(self._id_for_user_index(user_index)),
                "username": unique_user_name,
                "displayName": f"Test user {user_index}",
                "preferredLanguage": "en",
            }
            # We need to set lastname and password for the sake of UDM, but wire.com doesn't store these.
            properties |= {"lastname": "lastname", "password": "univention"}
            for i, email_attr in enumerate(email_attrs):
                email = f"{unique_user_name}-{i}@{maildomain}"
                if email_attr == "mailPrimaryAddress":
                    assert email_attr not in properties
                    properties[email_attr] = email
                else:
                    properties.setdefault(email_attr, []).append(email)
            properties |= override_properties
            return properties

        return factory

    @pytest.fixture
    def get_user(self, independent_client: SyncSCIMClient):
        def getter(user_index: int) -> User | None:
            assert user_index < NUM_TEST_USERS
            external_id = self._id_for_user_index(user_index)
            user_list = independent_client.query(
                User, query_parameters=SearchRequest(filter=ScimFilter(f'externalId eq "{external_id}"'))
            )
            assert isinstance(user_list, ListResponse)
            assert user_list.resources is not None
            assert 0 <= len(user_list.resources) <= 1
            for user in user_list.resources:
                return user
            return None

        return getter

    @pytest.fixture
    def wait_for_user(self, get_user: Callable[[int], User | None]):
        async def waiter(user_index: int, user_is_acceptable: Callable[[User | None], bool]) -> User | None:
            # wire.com has a weird issue where searching for a user at the wrong moment just after it's been created
            # leads to the user data being permanently message up (see
            # https://github.com/wireapp/wire-server/issues/5711). Wait 1 second before we try to find the user to
            # prevent this from happening.
            await asyncio.sleep(1)
            async with asyncio.timeout(10):
                while True:
                    user = await asyncio.to_thread(get_user, user_index)
                    if user_is_acceptable(user):
                        return user
                    await asyncio.sleep(0.05)

        return waiter

    @pytest.fixture
    def wait_for_user_to_match(
        self, wait_for_user: Callable[[int, Callable[[User | None], bool]], Awaitable[User | None]]
    ):
        async def waiter(user_index: int, matcher: Matcher) -> User:
            """
            Wait for a matching user to exist at wire.com.

            :param matcher: The matcher the user must match.
            """
            user = await wait_for_user(user_index, lambda u: matcher.matches(u))
            assert isinstance(user, User)
            return user

        return waiter

    @pytest.fixture
    def wait_for_user_to_exist(self, wait_for_user_to_match: Callable[[int, Matcher], Awaitable[User]]):
        async def waiter(user_index: int) -> User:
            """Wait for a user to exist at wire.com."""
            return await wait_for_user_to_match(user_index, anything())

        return waiter

    @pytest.fixture
    def wait_for_user_to_not_exist(
        self, wait_for_user: Callable[[int, Callable[[User | None], bool]], Awaitable[None]]
    ):
        async def waiter(user_index: int) -> None:
            """Wait until a user does not exist at wire.com."""
            await wait_for_user(user_index, lambda u: u is None)

        return waiter

    @pytest.fixture
    def wait_for_morgue_entry(self, database: DBSession):
        async def waiter(udm_object: Object) -> None:
            object_id = udm_object.properties["univentionObjectIdentifier"]
            with database:
                async with asyncio.timeout(10):
                    while True:
                        morgue = await asyncio.to_thread(list, database.get_errors(object_id))
                        if len(morgue) > 1:
                            logger.warning(
                                "Found more than one entry in the morgue.", object_id=object_id, num_entries=len(morgue)
                            )
                        if morgue:
                            return
                        await asyncio.sleep(0.01)

        return waiter

    def _id_for_user_index(self, user_index: int) -> uuid.UUID:
        return uuid.UUID(int=user_index, version=4)  # UDM wants valid UUID1 or UUID4.

    async def test_create_simple_user(
        self,
        udm_object_janitor: UDMObjectJanitor,
        make_wire_com_user_properties: UserPropertiesFactory,
        wait_for_user_to_exist: Callable[[int], Awaitable[User]],
    ):
        async with BackgroundConsumer(), udm_object_janitor:
            properties = make_wire_com_user_properties(0, email_attrs=["mailPrimaryAddress"])
            udm_user = udm_object_janitor.create_udm_user(properties)
            actual_user = await wait_for_user_to_exist(0)
            assert_that(actual_user, expected_user_for_udm_user(udm_user))

    async def test_prefers_mail_primary_address_as_only_email_address(
        self,
        udm_object_janitor: UDMObjectJanitor,
        make_wire_com_user_properties: UserPropertiesFactory,
        wait_for_user_to_exist: Callable[[int], Awaitable[User]],
    ):
        # wire.com will only store one email address. The primary should be the first choice.
        async with BackgroundConsumer(), udm_object_janitor:
            properties = make_wire_com_user_properties(
                0, email_attrs=["mailPrimaryAddress", "mailAlternativeAddress", "e-mail"]
            )
            udm_user = udm_object_janitor.create_udm_user(properties)
            actual_user = await wait_for_user_to_exist(0)
            expected_email = Email(
                value=udm_user.properties["mailPrimaryAddress"], type=Email.Type("mailbox"), primary=False
            )
            assert_that(actual_user, expected_user_for_udm_user(udm_user, emails=[expected_email]))

    async def test_falls_back_to_mail_alternative_address(
        self,
        udm_object_janitor: UDMObjectJanitor,
        make_wire_com_user_properties: UserPropertiesFactory,
        wait_for_user_to_exist: Callable[[int], Awaitable[User]],
    ):
        async with BackgroundConsumer(), udm_object_janitor:
            properties = make_wire_com_user_properties(0, email_attrs=["mailAlternativeAddress", "e-mail"])
            udm_user = udm_object_janitor.create_udm_user(properties)
            actual_user = await wait_for_user_to_exist(0)
            expected_email = Email(
                value=udm_user.properties["mailAlternativeAddress"][0], type=Email.Type("alias"), primary=False
            )
            assert_that(actual_user, expected_user_for_udm_user(udm_user, emails=[expected_email]))

    async def test_falls_back_to_other_email_address(
        self,
        udm_object_janitor: UDMObjectJanitor,
        make_wire_com_user_properties: UserPropertiesFactory,
        wait_for_user_to_exist: Callable[[int], Awaitable[User]],
    ):
        async with BackgroundConsumer(), udm_object_janitor:
            properties = make_wire_com_user_properties(0, email_attrs=["e-mail"])
            udm_user = udm_object_janitor.create_udm_user(properties)
            actual_user = await wait_for_user_to_exist(0)
            expected_email = Email(value=udm_user.properties["e-mail"][0], type=Email.Type.other, primary=False)
            assert_that(actual_user, expected_user_for_udm_user(udm_user, emails=[expected_email]))

    async def test_creates_morgue_entry_if_no_email_address_given(
        self,
        udm_object_janitor: UDMObjectJanitor,
        make_wire_com_user_properties: UserPropertiesFactory,
        wait_for_morgue_entry: Callable[[Object], Awaitable[None]],
    ):
        # If we don't provide an email, wire.com will respond with an error, which results in a morgue entry.
        async with BackgroundConsumer(), udm_object_janitor:
            properties = make_wire_com_user_properties(0, email_attrs=[])
            udm_user = udm_object_janitor.create_udm_user(properties)
            await wait_for_morgue_entry(udm_user)

    @pytest.mark.parametrize("disabled", [True, False])
    async def test_always_creates_deactivated_users(
        self,
        udm_object_janitor: UDMObjectJanitor,
        make_wire_com_user_properties: UserPropertiesFactory,
        wait_for_user_to_exist: Callable[[int], Awaitable[User]],
        disabled: bool,
    ):
        # Even if we set active=True, wire.com sets it to False.
        async with BackgroundConsumer(), udm_object_janitor:
            properties = make_wire_com_user_properties(0, email_attrs=["mailPrimaryAddress"], disabled=disabled)
            udm_user = udm_object_janitor.create_udm_user(properties)
            actual_user = await wait_for_user_to_exist(0)
            assert_that(actual_user, expected_user_for_udm_user(udm_user, active=False))

    @pytest.mark.parametrize("udm_pref_lang,wire_pref_lang", [("de", "de"), ("es_ES", "es")])
    async def test_uses_only_first_2_chars_of_preferred_language(
        self,
        udm_object_janitor: UDMObjectJanitor,
        make_wire_com_user_properties: UserPropertiesFactory,
        wait_for_user_to_exist: Callable[[int], Awaitable[User]],
        udm_pref_lang: str,
        wire_pref_lang: str,
    ):
        # wire.com uses ISO 639-1 (2 letter) language codes. Any extra characters are ignored.
        async with BackgroundConsumer(), udm_object_janitor:
            properties = make_wire_com_user_properties(
                0, email_attrs=["mailPrimaryAddress"], preferredLanguage=udm_pref_lang
            )
            udm_user = udm_object_janitor.create_udm_user(properties)
            actual_user = await wait_for_user_to_exist(0)
            assert_that(actual_user, expected_user_for_udm_user(udm_user, preferred_language=wire_pref_lang))

    async def test_creates_morgue_entry_on_invalid_preferred_language(
        self,
        udm_object_janitor: UDMObjectJanitor,
        make_wire_com_user_properties: UserPropertiesFactory,
        wait_for_morgue_entry: Callable[[Object], Awaitable[None]],
    ):
        async with BackgroundConsumer(), udm_object_janitor:
            properties = make_wire_com_user_properties(
                0, email_attrs=["mailPrimaryAddress"], preferredLanguage="__invalid code"
            )
            udm_user = udm_object_janitor.create_udm_user(properties)
            await wait_for_morgue_entry(udm_user)

    @pytest.mark.parametrize("role_value", ValidWireComRoleValues)
    async def test_always_uses_member_role(
        self,
        udm_object_janitor: UDMObjectJanitor,
        make_wire_com_user_properties: UserPropertiesFactory,
        wait_for_user_to_exist: Callable[[int], Awaitable[User]],
        role_value: str,
    ):
        async with BackgroundConsumer(), udm_object_janitor:
            properties = make_wire_com_user_properties(
                0,
                email_attrs=["mailPrimaryAddress"],
                guardianRoles=[role_value],
                guardianInheritedRoles=[role_value],
            )
            udm_user = udm_object_janitor.create_udm_user(properties)
            actual_user = await wait_for_user_to_exist(0)
            assert_that(actual_user, expected_user_for_udm_user(udm_user, roles=[Role(value="member")]))

    async def test_creates_morgue_entry_on_invalid_role(
        self,
        udm_object_janitor: UDMObjectJanitor,
        make_wire_com_user_properties: UserPropertiesFactory,
        wait_for_morgue_entry: Callable[[Object], Awaitable[None]],
    ):
        async with BackgroundConsumer(), udm_object_janitor:
            properties = make_wire_com_user_properties(
                0,
                email_attrs=["mailPrimaryAddress"],
                guardianRoles=["this_is_not_a_valid_role"],
                guardianInheritedRoles=["neither_is_this"],
            )
            udm_user = udm_object_janitor.create_udm_user(properties)
            await wait_for_morgue_entry(udm_user)

    async def test_creates_morgue_entry_on_existing_username(
        self,
        udm_object_janitor: UDMObjectJanitor,
        make_wire_com_user_properties: UserPropertiesFactory,
        wait_for_morgue_entry: Callable[[Object], Awaitable[None]],
    ):
        async with BackgroundConsumer(), udm_object_janitor:
            properties = make_wire_com_user_properties(
                0, email_attrs=["mailPrimaryAddress"], username=ALREADY_EXISTING_USERNAME
            )
            udm_user = udm_object_janitor.create_udm_user(properties)
            await wait_for_morgue_entry(udm_user)

    async def test_update_user(
        self,
        udm_object_janitor: UDMObjectJanitor,
        make_wire_com_user_properties: UserPropertiesFactory,
        wait_for_user_to_exist: Callable[[int], Awaitable[User]],
        wait_for_user_to_match: Callable[[int, Matcher], Awaitable[User]],
    ):
        async with BackgroundConsumer(), udm_object_janitor:
            properties = make_wire_com_user_properties(0, email_attrs=["mailPrimaryAddress"])
            udm_user = udm_object_janitor.create_udm_user(properties)
            actual_user = await wait_for_user_to_exist(0)
            assert_that(actual_user, expected_user_for_udm_user(udm_user))

            # New properties, just to get a fresh email address.
            other_properties = make_wire_com_user_properties(0, email_attrs=["mailPrimaryAddress"])
            properties["mailPrimaryAddress"] = other_properties["mailPrimaryAddress"]
            properties["username"] = properties["username"] + "-modified"
            properties["displayName"] = properties["displayName"] + "-modified"
            properties["preferredLanguage"] = "de"
            properties["password"] = "new_password"  # Only needed so UDM doesn't complain.
            updated_udm_user = udm_object_janitor.update_udm_user(properties)
            actual_user = await wait_for_user_to_match(0, expected_user_for_udm_user(updated_udm_user))
            assert_that(actual_user, expected_user_for_udm_user(updated_udm_user))

    async def test_doesnt_update_roles(
        self,
        udm_object_janitor: UDMObjectJanitor,
        make_wire_com_user_properties: UserPropertiesFactory,
        wait_for_user_to_exist: Callable[[int], Awaitable[User]],
        wait_for_user_to_match: Callable[[int, Matcher], Awaitable[User]],
    ):
        async with BackgroundConsumer(), udm_object_janitor:
            properties = make_wire_com_user_properties(0, email_attrs=["mailPrimaryAddress"])
            udm_user = udm_object_janitor.create_udm_user(properties)
            actual_user = await wait_for_user_to_exist(0)
            assert_that(actual_user, expected_user_for_udm_user(udm_user, roles=[Role(value="member")]))
            properties["username"] = properties["username"] + "-modified"
            properties["guardianRoles"] = [ValidWireComRoleValues.partner]
            properties["password"] = "new_password"  # Only needed so UDM doesn't complain.
            updated_udm_user = udm_object_janitor.update_udm_user(properties)
            actual_user = await wait_for_user_to_match(
                0, expected_user_for_udm_user(updated_udm_user, roles=[Role(value="member")])
            )
            assert_that(actual_user, expected_user_for_udm_user(updated_udm_user, roles=[Role(value="member")]))

    async def test_delete_user(
        self,
        udm_object_janitor: UDMObjectJanitor,
        make_wire_com_user_properties: UserPropertiesFactory,
        wait_for_user_to_exist: Callable[[int], Awaitable[User]],
        wait_for_user_to_not_exist: Callable[[int], Awaitable[None]],
    ):
        async with BackgroundConsumer(), udm_object_janitor:
            properties = make_wire_com_user_properties(0, email_attrs=["mailPrimaryAddress"])
            udm_object_janitor.create_udm_user(properties)
            await wait_for_user_to_exist(0)
            udm_object_janitor.delete_udm_user(properties)
            await wait_for_user_to_not_exist(0)
