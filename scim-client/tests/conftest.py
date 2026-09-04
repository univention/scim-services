# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

from collections.abc import Generator
from pathlib import Path

import pytest

from univention.provisioning.error_handling.db import DBSession, initialize_db


@pytest.fixture
def database(tmp_path: Path) -> Generator[DBSession, None, None]:
    db_path = tmp_path / "scim-client.db"
    database = DBSession(f"sqlite:///{db_path}")
    initialize_db(database)

    yield database

    database.engine.dispose()
    db_path.unlink(missing_ok=True)


def pytest_addoption(parser):
    parser.addoption("--randomly-seed", help="Seed to use for Faker randomization.")
