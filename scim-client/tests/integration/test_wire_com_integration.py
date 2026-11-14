# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2026 Univention GmbH

import asyncio
import os
import time
import uuid
from collections.abc import Awaitable, Callable
from typing import Any, Literal, Protocol

import httpx2
import pytest
from hamcrest import all_of, assert_that, has_properties, instance_of
from hamcrest.core.matcher import Matcher
from loguru import logger
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


class UserPropertiesFactory(Protocol):
    def __call__(
        self, user_index: int, *, email_attrs: list[Literal["mailPrimaryAddress", "mailAlternativeAddress", "e-mail"]]
    ) -> dict[str, str]: ...


def expected_user_for_udm_user(udm_user: Object, *, active: bool) -> Matcher:
    return all_of(
        instance_of(User),
        has_properties(
            external_id=udm_user.properties["univentionObjectIdentifier"],
            user_name=udm_user.properties["username"],
            display_name=udm_user.properties["displayName"],
            preferred_language=udm_user.properties["preferredLanguage"],
            emails=[Email(value=udm_user.properties["mailPrimaryAddress"], type="mailbox", primary=False)],
            roles=[Role(value="member")],
            active=active,
        ),
    )


@pytest.mark.skipif(
    not _tests_should_be_run(), reason="Test has been deconfigured via TESTCONF_RUN_WIRE_COM_INTEGRATION_TESTS=false."
)
@pytest.mark.wire_com_integration_tests
class TestWireComIntegration:
    @pytest.fixture
    def wire_com_scim_bearer_token(self):
        return os.environ["TESTCONF_WIRE_COM_SCIM_BEARER_TOKEN"]

    @pytest.fixture(autouse=True)
    def set_up_env(self, monkeypatch: pytest.MonkeyPatch, wire_com_scim_bearer_token):
        monkeypatch.setenv("SCIM_SERVER_BASE_URL", WIRE_COM_SCIM_SERVER_BASE_URL)
        monkeypatch.setenv("SCIM_AUTH_METHOD", AuthMethod.BEARER)
        monkeypatch.setenv("SCIM_BEARER_TOKEN", wire_com_scim_bearer_token)

    @pytest.fixture
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
                f"Found existing test users {existing_test_users}. Is there another test going on right now? We'll "
                "wait a while to let it finish."
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
                logger.info(f"Deleting user {user.external_id} after tests.")
                independent_client.delete(user)

    @pytest.fixture
    def make_wire_com_user_properties(self, maildomain: str) -> UserPropertiesFactory:
        def factory(
            user_index: int, *, email_attrs: list[Literal["mailPrimaryAddress", "mailAlternativeAddress", "e-mail"]]
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
                if email_attr == "e-mail":
                    properties.setdefault("e-mail", []).append(email)
                else:
                    assert email_attr not in properties
                    properties[email_attr] = email
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
        async def getter(user_index: int) -> User:
            # wire.com has a weird issue where searching for a user at the wrong moment just after it's been created
            # leads to the user data being permanently message up (see
            # https://github.com/wireapp/wire-server/issues/5711). Wait 1 second before we try to find the user to
            # prevent this from happening.
            await asyncio.sleep(1)
            async with asyncio.timeout(10):
                while True:
                    if (user := await asyncio.to_thread(get_user, user_index)) is not None:
                        return user
                    await asyncio.sleep(0.05)

        return getter

    def _id_for_user_index(self, user_index: int) -> uuid.UUID:
        """Create a deterministic external ID for the user."""
        return uuid.UUID(int=user_index, version=4)  # UDM wants valid UUID1 or UUID4.

    async def test_create_user(
        self,
        udm_object_janitor: UDMObjectJanitor,
        make_wire_com_user_properties: UserPropertiesFactory,
        wait_for_user: Callable[[int], Awaitable[User]],
    ):
        async with BackgroundConsumer(), udm_object_janitor as janitor:
            properties = make_wire_com_user_properties(0, email_attrs=["mailPrimaryAddress"])
            udm_user = janitor.create_udm_user(properties)
            actual_user = await wait_for_user(0)
            assert_that(actual_user, expected_user_for_udm_user(udm_user, active=False))
