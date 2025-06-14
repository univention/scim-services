# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

import os

import pytest

from univention.scim.consumer.message_handler import handle_udm_message
from univention.scim.consumer.scim_client import ScimClientNoDataFoundException

from ..data.provisioning_message_factory import get_provisioning_message


@pytest.fixture(scope="function")
def set_scim_user_filter_attribute():
    #
    # Enable filter on field isNextcloudUser
    #
    os.environ["SCIM_USER_FILTER_ATTRIBUTE"] = "isNextcloudUser"

    yield

    #
    # Disable filter on field isNextcloudUser
    #
    os.environ.pop("SCIM_USER_FILTER_ATTRIBUTE")


@pytest.mark.asyncio
async def test_create_user(set_scim_user_filter_attribute, scim_client):
    #
    # Create user
    #
    pm = get_provisioning_message("user_create")
    pm.body.new["properties"]["isNextcloudUser"] = True

    await handle_udm_message(pm)

    user = scim_client.get_resource_by_external_id(pm.body.new["properties"].get("univentionObjectIdentifier"))

    assert user.user_name == pm.body.new["properties"].get("username")

    #
    # Update user
    #
    pm = get_provisioning_message("user_update")
    pm.body.new["properties"]["isNextcloudUser"] = True

    await handle_udm_message(pm)

    user = scim_client.get_resource_by_external_id(pm.body.new["properties"].get("univentionObjectIdentifier"))

    assert user.user_name == pm.body.new["properties"].get("username")

    #
    # Delete user
    #
    pm = get_provisioning_message("user_delete")
    pm.body.old["properties"]["isNextcloudUser"] = True

    await handle_udm_message(pm)

    with pytest.raises(ScimClientNoDataFoundException):
        user = scim_client.get_resource_by_external_id(pm.body.old["properties"].get("univentionObjectIdentifier"))


@pytest.mark.asyncio
async def test_create_user_with_update(set_scim_user_filter_attribute, scim_client):
    #
    # Create user, should not created in SCIM
    #
    pm = get_provisioning_message("user_create")
    pm.body.new["properties"]["isNextcloudUser"] = False

    await handle_udm_message(pm)

    with pytest.raises(ScimClientNoDataFoundException):
        user = scim_client.get_resource_by_external_id(pm.body.new["properties"].get("univentionObjectIdentifier"))

    #
    # Update user, should created in SCIM
    #
    pm = get_provisioning_message("user_update")
    pm.body.old["properties"]["isNextcloudUser"] = False
    pm.body.new["properties"]["isNextcloudUser"] = True

    await handle_udm_message(pm)

    user = scim_client.get_resource_by_external_id(pm.body.new["properties"].get("univentionObjectIdentifier"))

    assert user.user_name == pm.body.new["properties"].get("username")

    #
    # Update user, should be deleted in SCIM
    #
    pm = get_provisioning_message("user_update")
    pm.body.old["properties"]["isNextcloudUser"] = True

    await handle_udm_message(pm)

    with pytest.raises(ScimClientNoDataFoundException):
        user = scim_client.get_resource_by_external_id(pm.body.new["properties"].get("univentionObjectIdentifier"))


@pytest.mark.asyncio
async def test_not_create_user(set_scim_user_filter_attribute, scim_client):
    #
    # Create user, should not created in SCIM
    #
    pm = get_provisioning_message("user_create")
    pm.body.new["properties"]["isNextcloudUser"] = False

    await handle_udm_message(pm)

    with pytest.raises(ScimClientNoDataFoundException):
        scim_client.get_resource_by_external_id(pm.body.new["properties"].get("univentionObjectIdentifier"))

    #
    # Update user, should not created in SCIM
    #
    pm = get_provisioning_message("user_update")
    pm.body.old["properties"]["isNextcloudUser"] = False
    pm.body.new["properties"]["isNextcloudUser"] = False

    await handle_udm_message(pm)

    with pytest.raises(ScimClientNoDataFoundException):
        scim_client.get_resource_by_external_id(pm.body.new["properties"].get("univentionObjectIdentifier"))
