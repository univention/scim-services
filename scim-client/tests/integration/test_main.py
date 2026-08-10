# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

from typing import Any

import pytest
from univention.admin.rest.client import UDM

from univention.scim.client.scim_client import ScimConsumer
from univention.scim.client.scim_http_client import ScimClient

from ..data.scim_helper import wait_for_resource_deleted, wait_for_resource_exists, wait_for_resource_updated
from ..data.udm_helper import (
    create_udm_group,
    create_udm_user,
    delete_udm_group,
    delete_udm_user,
    update_udm_group,
    update_udm_user,
)


def test_user_crud(
    udm_client: UDM,
    background_scim_client: ScimConsumer,
    scim_http_client: ScimClient,
    user_data: dict[str, Any],
    user_data_updated: dict[str, Any],
) -> None:
    assert background_scim_client

    # Test create
    udm_user = create_udm_user(udm_client=udm_client, user_data=user_data)
    user: dict = wait_for_resource_exists(scim_http_client, udm_user)
    assert user
    assert user["userName"] == user_data.get("username")

    # Test update
    udm_user = update_udm_user(udm_client=udm_client, user_data=user_data_updated)
    user = wait_for_resource_updated(
        scim_http_client=scim_http_client,
        udm_object=udm_user,
        condition_attr="displayName",
        condition_val=user_data_updated.get("displayName"),
    )
    assert user
    assert user["displayName"] == user_data_updated.get("displayName")

    # Test delete
    udm_user = delete_udm_user(udm_client=udm_client, user_data=user_data)
    assert wait_for_resource_deleted(scim_http_client, udm_user)


def test_user_with_extensions(
    udm_client: UDM,
    background_scim_client: ScimConsumer,
    scim_http_client: ScimClient,
    user_data_with_extensions: dict[str, Any],
) -> None:
    assert background_scim_client

    # Test create
    udm_user = create_udm_user(udm_client=udm_client, user_data=user_data_with_extensions)
    user: dict = wait_for_resource_exists(scim_http_client, udm_user)
    assert user
    assert user["userName"] == user_data_with_extensions.get("username")
    assert user["urn:ietf:params:scim:schemas:extension:enterprise:2.0:User"][
        "employeeNumber"
    ] == user_data_with_extensions.get("employeeNumber")

    # Cleanup
    udm_user = delete_udm_user(udm_client=udm_client, user_data=user_data_with_extensions)
    assert wait_for_resource_deleted(scim_http_client, udm_user)


def test_add_group_member(
    udm_client: UDM,
    background_scim_client: ScimConsumer,
    group_data: dict[str, Any],
    user_data: dict[str, Any],
    scim_http_client: ScimClient,
) -> None:
    assert background_scim_client

    #
    # Create group
    #
    udm_group = create_udm_group(udm_client=udm_client, group_data=group_data)
    group: dict = wait_for_resource_exists(scim_http_client, udm_group)
    assert group
    assert group["displayName"] == group_data.get("name")

    #
    # Create user
    #
    udm_user_ret = create_udm_user(udm_client=udm_client, user_data=user_data)
    user: dict = wait_for_resource_exists(scim_http_client, udm_user_ret)
    assert user
    assert user["userName"] == user_data.get("username")

    #
    # Update group member
    #
    group_data["users"].append(udm_user_ret.dn)
    group_data["name"] = f"{group_data.get('name')} - Updated"

    udm_group = update_udm_group(udm_client=udm_client, group_data=group_data)
    group = wait_for_resource_updated(
        scim_http_client=scim_http_client,
        udm_object=udm_group,
        condition_attr="displayName",
        condition_val=None,
        condition_func=lambda resource: resource["displayName"] == group_data.get("name")
        and len(resource.get("members", [])) == 1,
    )

    assert group
    assert group["displayName"] == group_data.get("name")
    assert group["members"][0]["value"] == user["id"]

    #
    # Cleanup
    #
    udm_user = delete_udm_user(udm_client=udm_client, user_data=user_data)
    assert wait_for_resource_deleted(scim_http_client, udm_user)

    udm_group = delete_udm_group(udm_client=udm_client, group_data=group_data)
    assert wait_for_resource_deleted(scim_http_client, udm_group)


@pytest.mark.skip("No impact at the moment. Activate again when needed.")
def test_update_group_member_dn(
    udm_client: UDM,
    background_scim_client: ScimConsumer,
    group_data: dict[str, Any],
    user_data: dict[str, Any],
    scim_http_client: ScimClient,
) -> None:
    assert background_scim_client

    #
    # Create user
    #
    udm_user = create_udm_user(udm_client=udm_client, user_data=user_data)
    assert wait_for_resource_exists(scim_http_client, udm_user)

    #
    # Create group with user as member
    #
    group_data["users"].append(udm_user.dn)
    udm_group = create_udm_group(udm_client=udm_client, group_data=group_data)
    assert wait_for_resource_exists(scim_http_client, udm_group)

    #
    # Update users dn
    #
    user_data["username"] = "username.moved.dn"
    user_data["password"] = None

    udm_user = update_udm_user(udm_client=udm_client, user_data=user_data)

    assert wait_for_resource_updated(
        scim_http_client=scim_http_client,
        udm_object=udm_user,
        condition_attr="userName",
        condition_val=user_data.get("username"),
    )

    #
    # Check group membership
    #

    # !!! No provisioning message !!!

    #
    # Cleanup
    #
    udm_user = delete_udm_user(udm_client=udm_client, user_data=user_data)
    assert wait_for_resource_deleted(scim_http_client, udm_user)

    udm_group = delete_udm_group(udm_client=udm_client, group_data=group_data)
    assert wait_for_resource_deleted(scim_http_client, udm_group)


@pytest.mark.skip("Will be developed further in a future MR")
def test_prefilled_sync(scim_http_client: ScimClient, create_user_and_group: Any) -> None:
    udm_users, udm_group = create_user_and_group

    user_ids = []
    for udm_user in udm_users:
        user: dict = wait_for_resource_exists(scim_http_client, udm_user)
        assert user
        user_ids.append(user["id"])

    assert len(udm_users) == len(user_ids)

    group: dict = wait_for_resource_exists(scim_http_client, udm_group)
    assert group
    group_members = []
    for group_member in group.get("members", []):
        group_members.append(group_member["value"])

    assert set(group_members) == set(user_ids)
