# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2026 Univention GmbH

import pathlib

import pytest


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    # Mark all tests in this directory.
    this_directory = pathlib.Path(__file__).resolve().parent
    for item in items:
        if item.path.resolve().is_relative_to(this_directory):
            item.add_marker(pytest.mark.unittest)
