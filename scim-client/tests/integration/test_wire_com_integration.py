# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2026 Univention GmbH

import asyncio
import multiprocessing
import os
import time
import uuid
from collections.abc import Awaitable, Callable
from typing import Protocol

import httpx2
import pytest
from aiohttp import ClientResponseError
from hamcrest import all_of, assert_that, has_properties, instance_of
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
from univention.admin.rest.client import UDM
from univention.provisioning.consumer.api import (
    ProvisioningConsumerClient,
    ProvisioningConsumerClientSettings,
    RealmTopic,
)

from univention.scim.client.authentication import AuthMethod, BearerAuth, BearerAuthSettings
from univention.scim.client.main import run as scim_client_run

from ..data.udm_helper import create_udm_user, delete_udm_user


NUM_TEST_USERS = 1
WIRE_COM_SCIM_SERVER_BASE_URL = "https://prod-nginz-https.wire.com/scim/v2"


class UserFactory(Protocol):
    def __call__(self, user_index: int, *, email_type) -> User: ...


def equivalent_user(user: User, active: bool):
    return all_of(
        instance_of(User),
        has_properties(
            external_id=user.external_id,
            user_name=user.user_name,
            name=user.name,
            display_name=user.display_name,
            preferred_language=user.preferred_language,
            emails=user.emails,
            roles=user.roles,
            active=active,
        ),
    )


class TestWireComIntegration:
    @pytest.fixture
    def wire_com_scim_bearer_token(self):
        return os.environ["WIRE_COM_SCIM_BEARER_TOKEN"]

    @pytest.fixture(autouse=True)
    def set_up_env(self, monkeypatch: pytest.MonkeyPatch, wire_com_scim_bearer_token):
        monkeypatch.setenv("PROVISIONING_DB", "sqlite:////tmp/scim-client.db")
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
    def make_wire_com_user(self, maildomain: str) -> UserFactory:
        def factory(user_index: int, *, email_type) -> User:
            assert user_index < NUM_TEST_USERS
            unique_user_name = f"univention-test-user-{user_index}-{uuid.uuid4()}"
            return User(
                external_id=str(self._id_for_user_index(user_index)),
                user_name=unique_user_name,
                display_name=f"Test user {user_index}",
                preferred_language="en",
                emails=[Email(value=f"{unique_user_name}@{maildomain}", type=email_type, primary=False)],
                roles=[Role(value="member")],
            )

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

    @pytest.mark.asyncio
    async def test_create_user(
        self, make_wire_com_user: UserFactory, udm_client: UDM, wait_for_user: Callable[[int], Awaitable[User]]
    ):
        admin_settings = ProvisioningConsumerClientSettings(
            provisioning_api_base_url=os.environ["PROVISIONING_API_BASE_URL"],
            provisioning_api_username=os.environ["PROVISIONING_API_ADMIN_USERNAME"],
            provisioning_api_password=os.environ["PROVISIONING_API_ADMIN_PASSWORD"],
            log_level="DEBUG",
        )
        async with ProvisioningConsumerClient(admin_settings) as admin_client:
            try:
                await admin_client.create_subscription(
                    name=os.environ["PROVISIONING_API_USERNAME"],
                    password=os.environ["PROVISIONING_API_PASSWORD"],
                    realms_topics=[
                        RealmTopic(realm="udm", topic="users/user"),
                        RealmTopic(realm="udm", topic="groups/group"),
                    ],
                    # do not request prefill to speed up tests, in the tests we are only interested
                    # in the new users/groups created within the test not all the default users/groups
                    request_prefill=False,
                )
            except ClientResponseError as e:
                logger.warning("%s, Client already exists", e)
            else:
                logger.info("Subscription {} created.", os.environ["PROVISIONING_API_USERNAME"])

        proc = multiprocessing.Process(target=scim_client_run)
        proc.start()
        try:
            expected_user = make_wire_com_user(0, email_type="mailbox")
            properties = {
                "univentionObjectIdentifier": expected_user.external_id,
                "username": expected_user.user_name,
                "displayName": expected_user.display_name,
                "preferredLanguage": expected_user.preferred_language,
                "mailPrimaryAddress": expected_user.emails[0].value,
            }
            properties |= {"lastname": "lastname", "password": "univention"}
            create_udm_user(udm_client=udm_client, user_data=properties)
            actual_user = await wait_for_user(0)
            assert_that(actual_user, equivalent_user(expected_user, active=False))

            # Cleanup.
            delete_udm_user(udm_client=udm_client, user_data=properties)
        finally:
            proc.terminate()
            admin_settings = ProvisioningConsumerClientSettings(
                provisioning_api_base_url=os.environ["PROVISIONING_API_BASE_URL"],
                provisioning_api_username=os.environ["PROVISIONING_API_ADMIN_USERNAME"],
                provisioning_api_password=os.environ["PROVISIONING_API_ADMIN_PASSWORD"],
                log_level="DEBUG",
            )
            async with ProvisioningConsumerClient(admin_settings) as admin_client:
                await admin_client.cancel_subscription(name=os.environ["PROVISIONING_API_USERNAME"])
                logger.info("Subscription {} deleted.", os.environ["PROVISIONING_API_USERNAME"])
