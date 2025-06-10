# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

import time
from datetime import UTC, datetime

import pytest
from faker import Faker
from fastapi.testclient import TestClient

from helpers.udm_client import MockUdm
from univention.scim.server.models.types import GroupWithExtensions


# Always use the mock UDM for mapping tests to allow easy adding of groups or users
# for the invalid members test it is required because real UDM does not allow to add
# a invalid user to a group
@pytest.fixture
def force_mock() -> bool:
    return True


udm_properties = {
    "name": "Test group",
    "description": "This is a test group",
    "guardianMemberRoles": ["member_role_2", "member_role_5"],
}

scim_schema = {
    "schemas": [
        "urn:ietf:params:scim:schemas:core:2.0:Group",
        "urn:ietf:params:scim:schemas:extension:Univention:1.0:Group",
    ],
    "displayName": "Test group",
    "urn:ietf:params:scim:schemas:extension:Univention:1.0:Group": {
        "description": "This is a test group",
        "memberRoles": [
            {"type": "guardian", "value": "member_role_2"},
            {"type": "guardian", "value": "member_role_5"},
        ],
    },
}


def test_get_group_mapping(udm_client: MockUdm, client: TestClient) -> None:
    fake = Faker()

    user_1 = udm_client.add_user()
    user_2 = udm_client.add_user()
    nested_group = udm_client.add_group()
    group = udm_client.add_raw_group(
        {
            **udm_properties,
            "createTimestamp": int(time.time()),
            "modifyTimestamp": int(time.time()),
            "univentionObjectIdentifier": fake.uuid4(),
            "users": [
                user_1.dn,
                user_2.dn,
            ],
            "nestedGroup": [nested_group.dn],
        }
    )

    create_date_time = datetime.fromtimestamp(group.properties["createTimestamp"], tz=UTC)
    modify_date_time = datetime.fromtimestamp(group.properties["modifyTimestamp"], tz=UTC)
    expected_data = {
        **scim_schema,
        "id": group.properties["univentionObjectIdentifier"],
        "externalId": group.properties["univentionObjectIdentifier"],
        "meta": {
            "resourceType": "Group",
            "created": f"{create_date_time.replace(microsecond=0, tzinfo=None).isoformat()}Z",
            "lastModified": f"{modify_date_time.replace(microsecond=0, tzinfo=None).isoformat()}Z",
            "location": f"https://scim.unit.test/scim/v2/Groups/{group.properties['univentionObjectIdentifier']}",
            "version": "1.0",
        },
        "members": [
            {
                "type": "User",
                "display": user_1.properties["displayName"],
                "value": user_1.properties["univentionObjectIdentifier"],
                "$ref": f"https://scim.unit.test/scim/v2/Users/{user_1.properties['univentionObjectIdentifier']}",
            },
            {
                "type": "User",
                "display": user_2.properties["displayName"],
                "value": user_2.properties["univentionObjectIdentifier"],
                "$ref": f"https://scim.unit.test/scim/v2/Users/{user_2.properties['univentionObjectIdentifier']}",
            },
            {
                "type": "Group",
                "display": nested_group.properties["name"],
                "value": nested_group.properties["univentionObjectIdentifier"],
                "$ref": f"https://scim.unit.test/scim/v2/Groups/{nested_group.properties['univentionObjectIdentifier']}",
            },
        ],
    }

    # Get the group
    response = client.get(f"/scim/v2/Groups/{group.properties['univentionObjectIdentifier']}")

    assert response.status_code == 200
    assert expected_data == response.json()


def test_create_group_mapping(udm_client: MockUdm, client: TestClient) -> None:
    user_1 = udm_client.add_user()
    user_2 = udm_client.add_user()
    nested_group = udm_client.add_group()

    test_group = GroupWithExtensions.model_validate(
        {
            **scim_schema,
            "members": [
                {
                    "type": "User",
                    "display": user_1.properties["displayName"],
                    "value": user_1.properties["univentionObjectIdentifier"],
                },
                {
                    "type": "User",
                    "display": user_2.properties["displayName"],
                    "value": user_2.properties["univentionObjectIdentifier"],
                    "$ref": f"https://scim.unit.test/scim/v2/Users/{user_2.properties['univentionObjectIdentifier']}",
                },
                {
                    "type": "Group",
                    "display": nested_group.properties["name"],
                    "value": nested_group.properties["univentionObjectIdentifier"],
                },
            ],
        }
    )

    response = client.post("/scim/v2/Groups", json=test_group.model_dump(by_alias=True, exclude_none=True))
    assert response.status_code == 201
    response_data = response.json()

    expected_properties = {
        **udm_properties,
        "univentionObjectIdentifier": response_data["id"],
        "users": [
            user_1.dn,
            user_2.dn,
        ],
        "nestedGroup": [nested_group.dn],
    }

    created_group = next(
        x.open()
        for x in udm_client.groups.values()
        if x.open().properties["univentionObjectIdentifier"] == response_data["id"]
    )
    assert created_group is not None
    assert expected_properties == created_group.properties


def test_get_group_with_invalid_member(udm_client: MockUdm, client: TestClient) -> None:
    group = udm_client.add_group(
        ["cn=invalid_user_1,ou=user,dc=example,dc=test", "cn=invalid_user_2,ou=user,dc=example,dc=test"]
    )

    # Get the group
    response = client.get(f"/scim/v2/Groups/{group.properties['univentionObjectIdentifier']}")

    assert response.status_code == 200
    data = response.json()

    # Verify response data
    # If mapping from UDM to SCIM we ignore invalid users/groups and just remove them from the list
    assert len(data["members"]) == 0
