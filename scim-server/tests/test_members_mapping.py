# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

import pytest
from fastapi.testclient import TestClient

from helpers.udm_client import MockUdm


# We can only test this with the mocked UDM because a real UDM
# does not allow creating a group with invalid members
@pytest.fixture
def force_mock() -> bool:
    return True


def test_get_group_with_invalid_member(force_mock: bool, udm_client: MockUdm, client: TestClient) -> None:
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
