# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH


def pytest_addoption(parser):
    parser.addoption("--randomly-seed", help="Seed to use for Faker randomization.")
