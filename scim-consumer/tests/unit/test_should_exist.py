# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

import pytest

from univention.scim.consumer.scim_consumer import should_exist_in_scim

from ..data.provisioning_message_factory import get_provisioning_message


should_exist_in_scim_testdata = [
    ("user_create", "isNcUser", True, True, True),
    ("user_create", "isNcUser", True, False, True),
    ("user_create", "isNcUser", False, True, False),
    ("user_create", "isNcUser", False, False, False),
    ("user_create", None, True, True, True),
    ("user_create", None, True, False, True),
    ("user_create", None, False, True, True),
    ("user_create", None, False, False, True),
    #
    ("user_update", "isNcUser", True, True, True),
    ("user_update", "isNcUser", True, False, True),
    ("user_update", "isNcUser", False, True, False),
    ("user_update", "isNcUser", False, False, False),
    ("user_update", None, True, True, True),
    ("user_update", None, True, False, True),
    ("user_update", None, False, True, True),
    ("user_update", None, False, False, True),
    #
    ("user_delete", "isNcUser", True, True, False),
    ("user_delete", "isNcUser", True, False, False),
    ("user_delete", "isNcUser", False, True, False),
    ("user_delete", "isNcUser", False, False, False),
    ("user_delete", None, True, True, False),
    ("user_delete", None, True, False, False),
    ("user_delete", None, False, True, False),
    ("user_delete", None, False, False, False),
]


@pytest.mark.parametrize(
    "pm_type, user_filter_attribute, is_user_filter_attribute_new, is_user_filter_attribute_old, expected_state",
    should_exist_in_scim_testdata,
)
def test_should_exist_in_scim(
    pm_type, user_filter_attribute, is_user_filter_attribute_new, is_user_filter_attribute_old, expected_state
):
    pm = get_provisioning_message(pm_type)

    if user_filter_attribute:
        if pm.body.new:
            pm.body.new["properties"][user_filter_attribute] = is_user_filter_attribute_new
        if pm.body.old:
            pm.body.old["properties"][user_filter_attribute] = is_user_filter_attribute_old

    actual = should_exist_in_scim(message=pm, user_filter_attribute=user_filter_attribute)

    assert actual == expected_state
