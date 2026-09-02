# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2026 Univention GmbH
"""The UDM property mapped to SCIM externalId is chosen per resource type.

`external_id_user_mapping` and `external_id_group_mapping` are configured separately,
so every lookup has to pick the one matching the message topic.
"""

from unittest.mock import MagicMock

import pytest

from univention.scim.client.scim_client import ScimConsumer
from univention.scim.client.scim_client_settings import ScimConsumerSettings


@pytest.fixture
def consumer() -> tuple[ScimConsumer, MagicMock]:
    settings = ScimConsumerSettings(
        scim_server_base_url="https://example.org/scim/v2",
        scim_auth_method="none",
        health_check_enabled=False,
        external_id_user_mapping="univentionObjectIdentifier",
        external_id_group_mapping="groupObjectId",
    )
    scim_http_client = MagicMock()
    return ScimConsumer(scim_http_client, MagicMock(), settings), scim_http_client


@pytest.mark.parametrize(
    ("topic", "expected"),
    [("users/user", "U-1"), ("groups/group", "G-7")],
)
def test_delete_looks_up_by_the_mapping_of_its_topic(
    consumer: tuple[ScimConsumer, MagicMock], topic: str, expected: str
) -> None:
    scim_consumer, scim_http_client = consumer
    scim_http_client.get_resource.return_value = {"id": "1", "externalId": expected}
    udm_object = type("Obj", (object,), {"properties": {"univentionObjectIdentifier": "U-1", "groupObjectId": "G-7"}})()

    scim_consumer.delete(udm_object, topic)

    assert scim_http_client.get_resource.call_args.args[0] == expected


def test_delete_rejects_an_object_without_the_mapped_property(
    consumer: tuple[ScimConsumer, MagicMock],
) -> None:
    scim_consumer, _ = consumer
    udm_object = type("Obj", (object,), {"properties": {"univentionObjectIdentifier": "U-1"}})()

    with pytest.raises(ValueError, match="groupObjectId"):
        scim_consumer.delete(udm_object, "groups/group")
