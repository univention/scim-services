# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

from typing import Any

from pytest_mock import MockerFixture
from univention.admin.rest.client import UDM

from univention.scim.consumer.group_membership_resolver import GroupMembershipLdapResolver
from univention.scim.consumer.scim_client import ScimClient
from univention.scim.consumer.scim_consumer import ScimConsumer

from ..data.scim_helper import wait_for_resource_deleted, wait_for_resource_exists
from ..data.udm_helper import create_udm_user, delete_udm_user


def test_get_univention_object_identifier_by_dn(
    group_membership_resolver: GroupMembershipLdapResolver, udm_client: UDM, user_data: dict[str, Any]
) -> None:
    udm_user = create_udm_user(udm_client=udm_client, user_data=user_data)

    univention_object_identifier = group_membership_resolver.get_univention_object_identifier_by_dn(
        "uid=testuser,cn=users,dc=univention-organization,dc=intranet"
    )

    assert univention_object_identifier == udm_user.properties.get("univentionObjectIdentifier")

    delete_udm_user(udm_client=udm_client, user_data=user_data)


def test_get_user(
    background_scim_consumer: ScimConsumer,
    scim_client: ScimClient,
    group_membership_resolver: GroupMembershipLdapResolver,
    udm_client: UDM,
    user_data: dict[str, Any],
    mocker: MockerFixture,
) -> None:
    assert background_scim_consumer

    udm_user = create_udm_user(udm_client=udm_client, user_data=user_data)
    wait_for_resource_exists(
        scim_client=scim_client, univention_object_identifier=udm_user.properties.get("univentionObjectIdentifier")
    )
    mocker.patch.object(
        group_membership_resolver,
        "get_univention_object_identifier_by_dn",
        return_value=udm_user.properties.get("univentionObjectIdentifier"),
    )

    scim_user = group_membership_resolver.get_user(key=udm_user.dn)

    print(scim_user)
    delete_udm_user(udm_client=udm_client, user_data=user_data)
    wait_for_resource_deleted(
        scim_client=scim_client,
        univention_object_identifier=udm_user.properties.get("univentionObjectIdentifier"),
        max_attemps=5,
    )


def test_get_user_not_exists(group_membership_resolver: GroupMembershipLdapResolver, mocker: MockerFixture) -> None:
    mocker.patch.object(
        group_membership_resolver,
        "get_univention_object_identifier_by_dn",
        return_value="4711",
    )

    scim_user = group_membership_resolver.get_user(key="invalid.dn")

    assert not scim_user
