#!/bin/bash
 # SPDX-License-Identifier: AGPL-3.0-only
 # SPDX-FileCopyrightText: 2025 Univention GmbH


 cd scim-server
 uv sync

# FIXME: tests need to be run in isolation because when they are run all in the same session some are failing
# https://git.knut.univention.de/univention/dev/internal/team-nubus/-/issues/1236
# Examples of tests that fail in current run order if being ran in one session: (changes if execution is changed)
# * tests/unit/test_user.py::TestUserAPI::test_level4_filter_expression
# * tests/unit/test_user.py::TestUserAPI::test_level4_remove_with_filter
# * tests/unit/test_user.py::TestUserAPI::test_level5_pathless_operation
test_suites=(
  tests/unit/
  tests/e2e/
  tests/middlewares/
)

for test_suite in "${test_suites[@]}"
do
  uv run pytest "${test_suite}" || exit -1
done

uv run coverage xml --ignore-errors
