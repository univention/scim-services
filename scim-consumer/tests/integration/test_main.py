# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

import pytest

from ..data.scim_helper import wait_for_resource_deleted, wait_for_resource_exists, wait_for_resource_updated
from ..data.udm_helper import (
    create_udm_group,
    create_udm_user,
    delete_udm_group,
    delete_udm_user,
    update_udm_group,
    update_udm_user,
)


def test_user_crud(udm_client, background_scim_consumer, scim_client, user_data, user_data_updated):
    assert background_scim_consumer

    # Test create
    create_udm_user(udm_client=udm_client, user_data=user_data)
    user = wait_for_resource_exists(scim_client, user_data["univentionObjectIdentifier"])
    assert user.user_name == user_data.get("username")

    # Test update
    update_udm_user(udm_client=udm_client, user_data=user_data_updated)
    user = wait_for_resource_updated(
        scim_client=scim_client,
        univention_object_identifier=user_data["univentionObjectIdentifier"],
        condition_attr="display_name",
        condition_val=user_data_updated.get("displayName"),
    )
    assert user.display_name == user_data_updated.get("displayName")

    # Test delete
    delete_udm_user(udm_client=udm_client, user_data=user_data)
    is_deleted = wait_for_resource_deleted(scim_client, user_data["univentionObjectIdentifier"])
    assert is_deleted


def test_add_group_member(udm_client, background_scim_consumer, group_data, user_data, scim_client):
    assert background_scim_consumer

    #
    # Create group
    #
    create_udm_group(udm_client=udm_client, group_data=group_data)
    group = wait_for_resource_exists(scim_client, group_data["univentionObjectIdentifier"])

    assert group.display_name == group_data.get("name")

    #
    # Create user
    #
    udm_user_ret = create_udm_user(udm_client=udm_client, user_data=user_data)
    user = wait_for_resource_exists(scim_client, user_data["univentionObjectIdentifier"])

    assert user.user_name == user_data.get("username")

    #
    # Update group member
    #
    group_data["users"].append(udm_user_ret.dn)
    group_data["name"] = f"{group_data.get('name')} - Updated"

    update_udm_group(udm_client=udm_client, group_data=group_data)
    group = wait_for_resource_updated(
        scim_client=scim_client,
        univention_object_identifier=group_data["univentionObjectIdentifier"],
        condition_attr="display_name",
        condition_val=group_data.get("name"),
    )

    assert group.display_name == group_data.get("name")
    assert group.members[0].value == user.id

    #
    # Cleanup
    #
    delete_udm_user(udm_client=udm_client, user_data=user_data)
    wait_for_resource_deleted(scim_client, user_data["univentionObjectIdentifier"])

    delete_udm_group(udm_client=udm_client, group_data=group_data)
    wait_for_resource_deleted(scim_client, group_data["univentionObjectIdentifier"])


@pytest.mark.skip("No impact at the moment. Activate again when needed.")
def test_update_group_member_dn(udm_client, background_scim_consumer, group_data, user_data, scim_client):
    assert background_scim_consumer

    #
    # Create user
    #
    udm_user = create_udm_user(udm_client=udm_client, user_data=user_data)
    wait_for_resource_exists(scim_client, user_data["univentionObjectIdentifier"])

    #
    # Create group with user as member
    #
    group_data["users"].append(udm_user.dn)
    create_udm_group(udm_client=udm_client, group_data=group_data)
    wait_for_resource_exists(scim_client, group_data["univentionObjectIdentifier"])

    #
    # Update users dn
    #
    user_data["username"] = "username.moved.dn"
    user_data["password"] = None

    udm_user = update_udm_user(udm_client=udm_client, user_data=user_data)

    wait_for_resource_updated(
        scim_client=scim_client,
        univention_object_identifier=user_data["univentionObjectIdentifier"],
        condition_attr="user_name",
        condition_val=user_data.get("username"),
    )

    #
    # Check group membership
    #

    # !!! No provisioning message !!!

    #
    # Cleanup
    #
    delete_udm_user(udm_client=udm_client, user_data=user_data)
    wait_for_resource_deleted(scim_client, user_data["univentionObjectIdentifier"])

    delete_udm_group(udm_client=udm_client, group_data=group_data)
    wait_for_resource_deleted(scim_client, group_data["univentionObjectIdentifier"])


@pytest.mark.skip("Will be developed further in a future MR")
def test_prefilled_sync(background_scim_consumer_prefilled, scim_client):
    udm_users, udm_group = background_scim_consumer_prefilled

    user_ids = []
    for udm_user in udm_users:
        user = wait_for_resource_exists(scim_client, udm_user.properties.get("univentionObjectIdentifier"))
        user_ids.append(user.id)

    assert len(udm_users) == len(user_ids)

    group = wait_for_resource_exists(scim_client, udm_group.properties.get("univentionObjectIdentifier"))
    group_members = []
    for group_member in group.members:
        group_members.append(group_member.value)

    assert set(group_members) == set(user_ids)
