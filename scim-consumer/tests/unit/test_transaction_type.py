# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

import pytest

from univention.scim.consumer.message_handler import get_required_action
from univention.scim.consumer.scim_client import ScimClientNoDataFoundException

from ..data.provisioning_message_factory import get_provisioning_message


class mock_client:
    def get_resource_by_external_id(self, user_exists: bool):
        if not user_exists:
            raise ScimClientNoDataFoundException("User not found!")

        return user_exists


transaction_type_testdata = [
    ("user_create", True, None, False, "CREATE"),
    ("user_create", True, None, True, "UPDATE"),
    ("user_update", True, True, True, "UPDATE"),
    ("user_update", True, True, False, "CREATE"),
    ("user_update", True, False, False, "CREATE"),
    ("user_update", False, False, False, None),
    ("user_update", False, False, True, None),
    ("user_update", False, True, True, "DELETE"),
    ("user_update", False, True, False, None),
    ("user_update", True, False, True, "UPDATE"),
    ("user_delete", None, True, True, "DELETE"),
    ("user_delete", None, True, False, None),
    ("user_delete", None, False, True, None),  # <- Should never happen!
    ("user_delete", None, False, False, None),
]


@pytest.mark.parametrize(
    "pmType, isNcUserNew, isNcUserOld, userExists, expectedTransactionType", transaction_type_testdata
)
def test_get_required_action(pmType, isNcUserNew, isNcUserOld, userExists, expectedTransactionType):
    pm = get_provisioning_message(pmType)

    if pm.body.new:
        pm.body.new["properties"]["isNextcloudUser"] = isNcUserNew
    if pm.body.old:
        pm.body.old["properties"]["isNextcloudUser"] = isNcUserOld

    client = mock_client()

    transaction_type = get_required_action(
        message=pm,
        scim_client=client,
        scim_external_id=userExists,
        scim_user_filter_attribute="isNextcloudUser",
    )

    assert transaction_type == expectedTransactionType
