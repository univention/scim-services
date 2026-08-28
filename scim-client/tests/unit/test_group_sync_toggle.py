# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

from unittest.mock import MagicMock

import pytest

from univention.scim.client.scim_client import ScimConsumer
from univention.scim.client.scim_client_settings import ScimConsumerSettings

from ..data.provisioning_message_factory import get_provisioning_message


@pytest.fixture
def scim_http_client() -> MagicMock:
    return MagicMock()


def make_consumer(group_sync_enabled: bool, scim_http_client: MagicMock) -> ScimConsumer:
    settings = ScimConsumerSettings(
        scim_server_base_url="https://example.com/scim/v2",
        scim_auth_method="none",
        health_check_enabled=False,
        group_sync_enabled=group_sync_enabled,
    )
    return ScimConsumer(scim_http_client, group_membership_resolver=None, settings=settings)


@pytest.mark.asyncio
async def test_group_message_skipped_when_group_sync_disabled(scim_http_client: MagicMock) -> None:
    consumer = make_consumer(group_sync_enabled=False, scim_http_client=scim_http_client)
    consumer.write_udm_object = MagicMock()  # type: ignore[method-assign]
    message = get_provisioning_message("group_create")

    await consumer.handle_udm_message(message)

    consumer.write_udm_object.assert_not_called()


@pytest.mark.asyncio
async def test_group_message_processed_when_group_sync_enabled(scim_http_client: MagicMock) -> None:
    consumer = make_consumer(group_sync_enabled=True, scim_http_client=scim_http_client)
    consumer.write_udm_object = MagicMock()  # type: ignore[method-assign]
    message = get_provisioning_message("group_create")

    await consumer.handle_udm_message(message)

    consumer.write_udm_object.assert_called_once()


@pytest.mark.asyncio
async def test_user_message_processed_regardless_of_group_sync_setting(scim_http_client: MagicMock) -> None:
    consumer = make_consumer(group_sync_enabled=False, scim_http_client=scim_http_client)
    consumer.write_udm_object = MagicMock()  # type: ignore[method-assign]
    message = get_provisioning_message("user_create")

    await consumer.handle_udm_message(message)

    consumer.write_udm_object.assert_called_once()
