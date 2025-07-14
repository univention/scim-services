# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

import os

import pytest
from pytest_mock import MockerFixture

from univention.scim.consumer.scim_client import ScimClient, ScimClientNoDataFoundException
from univention.scim.consumer.scim_consumer import ScimConsumer

from ..data.provisioning_message_factory import get_provisioning_message


@pytest.mark.asyncio
async def test_create_group(scim_client: ScimClient, scim_consumer: ScimConsumer) -> None:
    #
    # Create Group
    #
    pm = get_provisioning_message("group_create")

    await scim_consumer.handle_udm_message(pm)

    group = scim_client.get_resource_by_external_id(pm.body.new["properties"].get("univentionObjectIdentifier"))

    assert group.display_name == pm.body.new["properties"].get("name")

    # Cleaning up
    scim_client.delete_resource(group)


@pytest.mark.asyncio
async def test_update_group(scim_client: ScimClient, scim_consumer: ScimConsumer) -> None:
    #
    # Create Group
    #
    pm = get_provisioning_message("group_create")
    await scim_consumer.handle_udm_message(pm)

    #
    # Update Group
    #
    pm = get_provisioning_message("group_update")
    await scim_consumer.handle_udm_message(pm)

    group = scim_client.get_resource_by_external_id(pm.body.new["properties"].get("univentionObjectIdentifier"))

    assert group.display_name == pm.body.new["properties"].get("name")

    # Cleaning up
    scim_client.delete_resource(group)


@pytest.mark.asyncio
async def test_delete_group(scim_client: ScimClient, scim_consumer: ScimConsumer) -> None:
    #
    # Create Group
    #
    pm = get_provisioning_message("group_create")
    await scim_consumer.handle_udm_message(pm)

    #
    # Delete Group
    #
    pm = get_provisioning_message("group_delete")
    await scim_consumer.handle_udm_message(pm)

    with pytest.raises(ScimClientNoDataFoundException):
        scim_client.get_resource_by_external_id(pm.body.old["properties"].get("univentionObjectIdentifier"))


@pytest.mark.asyncio
async def test_add_group_member(scim_client: ScimClient, scim_consumer: ScimConsumer, mocker: MockerFixture) -> None:
    #
    # Create User
    #
    pm_user = get_provisioning_message("user_create")
    await scim_consumer.handle_udm_message(pm_user)
    user = scim_client.get_resource_by_external_id(pm_user.body.new["properties"].get("univentionObjectIdentifier"))

    #
    # Create Group
    #
    pm_group = get_provisioning_message("group_create")
    await scim_consumer.handle_udm_message(pm_group)

    # Mock GroupMembershipLdapResolver.get_univention_object_identifier_by_dn()
    # because the record is not in LDAP!
    mocker.patch(
        "univention.scim.consumer.group_membership_resolver.GroupMembershipLdapResolver.get_univention_object_identifier_by_dn",
        return_value=pm_user.body.new["properties"].get("univentionObjectIdentifier"),
    )

    #
    # Add group member
    #
    pm_group = get_provisioning_message("group_update")
    pm_group.body.new["properties"]["users"] = [
        pm_user.body.new["dn"],
    ]
    await scim_consumer.handle_udm_message(pm_group)

    group = scim_client.get_resource_by_external_id(pm_group.body.new["properties"].get("univentionObjectIdentifier"))

    assert group.display_name == pm_group.body.new["properties"].get("name")
    assert group.members[0].value == user.id

    #
    # Cleaning up
    #
    scim_client.delete_resource(group)
    scim_client.delete_resource(user)


@pytest.mark.skipif(
    "UNIVENTION_SCIM_SERVER" in os.environ, reason="Not working with Univention SCIM server at the moment!"
)
@pytest.mark.asyncio
async def test_remove_group_member(scim_client: ScimClient, scim_consumer: ScimConsumer, mocker: MockerFixture) -> None:
    #
    # Create User
    #
    pm_user = get_provisioning_message("user_create")
    await scim_consumer.handle_udm_message(pm_user)
    user = scim_client.get_resource_by_external_id(pm_user.body.new["properties"].get("univentionObjectIdentifier"))

    #
    # Create Group
    #
    pm_group = get_provisioning_message("group_create")
    await scim_consumer.handle_udm_message(pm_group)

    # Mock GroupMembershipLdapResolver.get_univention_object_identifier_by_dn()
    # because the record is not in LDAP!
    mocker.patch(
        "univention.scim.consumer.group_membership_resolver.GroupMembershipLdapResolver.get_univention_object_identifier_by_dn",
        return_value=pm_user.body.new["properties"].get("univentionObjectIdentifier"),
    )

    #
    # Add group member
    #
    pm_group = get_provisioning_message("group_update")
    pm_group.body.new["properties"]["users"] = [
        pm_user.body.new["dn"],
    ]
    await scim_consumer.handle_udm_message(pm_group)

    #
    # Remove group member
    #
    pm_group = get_provisioning_message("group_update")
    pm_group.body.old["properties"]["users"] = [
        pm_user.body.new["dn"],
    ]
    await scim_consumer.handle_udm_message(pm_group)

    group = scim_client.get_resource_by_external_id(pm_group.body.new["properties"].get("univentionObjectIdentifier"))

    assert group.display_name == pm_group.body.new["properties"].get("name")
    assert len(group.members) == 0

    #
    # Cleaning up
    #
    scim_client.delete_resource(group)
    scim_client.delete_resource(user)
