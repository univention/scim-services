# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH


import pytest

from univention.scim.client.scim_client import ScimConsumer
from univention.scim.client.scim_http_client import ScimClient, ScimClientNoDataFoundException

from ..data.provisioning_message_factory import get_provisioning_message


@pytest.mark.asyncio
async def test_create_user(scim_http_client: ScimClient, scim_client: ScimConsumer) -> None:
    # Create user
    pm = get_provisioning_message("user_create")
    pm.body.new["properties"]["isNextcloudUser"] = True
    scim_client.settings.scim_user_filter_attribute = "isNextcloudUser"

    await scim_client.handle_udm_message(pm)

    user = scim_http_client.get_resource_by_external_id(pm.body.new["properties"].get("univentionObjectIdentifier"))
    assert user.user_name == pm.body.new["properties"].get("username")

    # Update user
    pm = get_provisioning_message("user_update")
    pm.body.new["properties"]["isNextcloudUser"] = True

    await scim_client.handle_udm_message(pm)

    user = scim_http_client.get_resource_by_external_id(pm.body.new["properties"].get("univentionObjectIdentifier"))
    assert user.user_name == pm.body.new["properties"].get("username")

    # Delete user
    pm = get_provisioning_message("user_delete")
    pm.body.old["properties"]["isNextcloudUser"] = True

    await scim_client.handle_udm_message(pm)

    with pytest.raises(ScimClientNoDataFoundException):
        user = scim_http_client.get_resource_by_external_id(pm.body.old["properties"].get("univentionObjectIdentifier"))


@pytest.mark.asyncio
async def test_create_user_with_update(scim_http_client: ScimClient, scim_client: ScimConsumer) -> None:
    #
    # Create user, should not created in SCIM
    #
    pm = get_provisioning_message("user_create")
    pm.body.new["properties"]["isNextcloudUser"] = False
    scim_client.settings.scim_user_filter_attribute = "isNextcloudUser"

    await scim_client.handle_udm_message(pm)

    with pytest.raises(ScimClientNoDataFoundException):
        user = scim_http_client.get_resource_by_external_id(pm.body.new["properties"].get("univentionObjectIdentifier"))

    #
    # Update user, should created in SCIM
    #
    pm = get_provisioning_message("user_update")
    pm.body.old["properties"]["isNextcloudUser"] = False
    pm.body.new["properties"]["isNextcloudUser"] = True

    await scim_client.handle_udm_message(pm)

    user = scim_http_client.get_resource_by_external_id(pm.body.new["properties"].get("univentionObjectIdentifier"))

    assert user.user_name == pm.body.new["properties"].get("username")

    #
    # Update user, should be deleted in SCIM
    #
    pm = get_provisioning_message("user_update")
    pm.body.old["properties"]["isNextcloudUser"] = True

    await scim_client.handle_udm_message(pm)

    with pytest.raises(ScimClientNoDataFoundException):
        user = scim_http_client.get_resource_by_external_id(pm.body.new["properties"].get("univentionObjectIdentifier"))


@pytest.mark.asyncio
async def test_not_create_user(scim_http_client: ScimClient, scim_client: ScimConsumer) -> None:
    #
    # Create user, should not created in SCIM
    #
    pm = get_provisioning_message("user_create")
    pm.body.new["properties"]["isNextcloudUser"] = False
    scim_client.settings.scim_user_filter_attribute = "isNextcloudUser"

    await scim_client.handle_udm_message(pm)

    with pytest.raises(ScimClientNoDataFoundException):
        scim_http_client.get_resource_by_external_id(pm.body.new["properties"].get("univentionObjectIdentifier"))

    #
    # Update user, should not created in SCIM
    #
    pm = get_provisioning_message("user_update")
    pm.body.old["properties"]["isNextcloudUser"] = False
    pm.body.new["properties"]["isNextcloudUser"] = False

    await scim_client.handle_udm_message(pm)

    with pytest.raises(ScimClientNoDataFoundException):
        scim_http_client.get_resource_by_external_id(pm.body.new["properties"].get("univentionObjectIdentifier"))
