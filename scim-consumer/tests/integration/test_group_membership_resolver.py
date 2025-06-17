# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

from univention.scim.consumer.group_membership_resolver import GroupMembershipLdapResolver

from ..data.scim_helper import wait_for_resource_deleted, wait_for_resource_exists
from ..data.udm_helper import create_udm_user, delete_udm_user


def test_get_univention_object_identifier_by_dn(scim_client, udm_client, user_data):
    udm_user = create_udm_user(udm_client=udm_client, user_data=user_data)

    resolver = GroupMembershipLdapResolver(scim_client)

    univention_object_identifier = resolver.get_univention_object_identifier_by_dn(
        "uid=testuser,cn=users,dc=univention-organization,dc=intranet"
    )

    assert univention_object_identifier == udm_user.properties.get("univentionObjectIdentifier")

    delete_udm_user(udm_client=udm_client, user_data=user_data)


def test_get_user(scim_consumer, scim_client, udm_client, user_data, mocker):
    assert scim_consumer

    udm_user = create_udm_user(udm_client=udm_client, user_data=user_data)
    wait_for_resource_exists(
        scim_client=scim_client, univention_object_identifier=udm_user.properties.get("univentionObjectIdentifier")
    )

    resolver = GroupMembershipLdapResolver(scim_client)
    mocker.patch.object(
        resolver,
        "get_univention_object_identifier_by_dn",
        return_value=udm_user.properties.get("univentionObjectIdentifier"),
    )

    scim_user = resolver.get_user(key=udm_user.dn)

    print(scim_user)

    delete_udm_user(udm_client=udm_client, user_data=user_data)
    wait_for_resource_deleted(
        scim_client=scim_client, univention_object_identifier=udm_user.properties.get("univentionObjectIdentifier")
    )


def test_get_user_not_exists(scim_client, mocker):
    resolver = GroupMembershipLdapResolver(scim_client)
    mocker.patch.object(
        resolver,
        "get_univention_object_identifier_by_dn",
        return_value="4711",
    )

    scim_user = resolver.get_user(key="invalid.dn")

    assert not scim_user
