# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2026 Univention GmbH
"""`_filter_by_names` prunes a mapped body against the target's advertised attributes.

Covers both containers a complex attribute is mapped into, a `dict` for a singular one
and a `list` of dicts for a multi-valued one, as well as the top-level case.
"""

from univention.scim.transformation.udm2scim import _filter_by_names


# A target advertising `name` and `emails` while declaring exactly one sub-attribute for
# each. Entries are lowercased because `UdmToScimMapper.__init__` normalizes the set
# before handing it to the filter.
SUPPORTED = frozenset({"name", "name.givenname", "emails", "emails.value"})


def test_undeclared_sub_attribute_of_a_complex_attribute_is_dropped() -> None:
    """`name` is singular, so its value is a dict."""
    data = {"name": {"givenName": "Admin", "formatted": "Admin Administrator"}}

    assert _filter_by_names(data, SUPPORTED) == {"name": {"givenName": "Admin"}}


def test_undeclared_sub_attribute_of_a_multi_valued_attribute_is_dropped() -> None:
    """`emails` is multi-valued, so its value is a list of dicts."""
    data = {"emails": [{"value": "admin@example.org", "type": "mailbox"}]}

    assert _filter_by_names(data, SUPPORTED) == {"emails": [{"value": "admin@example.org"}]}


def test_unadvertised_top_level_attribute_is_dropped_in_both_containers() -> None:
    """An attribute the target does not declare never reaches the body."""
    data = {"displayName": "Admin Administrator", "phoneNumbers": [{"value": "12345"}]}

    assert _filter_by_names(data, SUPPORTED) == {}
