# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2026 Univention GmbH

from collections.abc import Generator
from pathlib import Path

import pytest

from univention.provisioning.error_handling.db import DBSession, initialize_db


@pytest.fixture
def database(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Generator[DBSession]:
    """
    SQLite database for testing.

    Creates and initializes a new SQLite database in a temporary file. Also
    sets PROVISIONING_DB to the connection string so any tests reading from
    the environment can access it.
    """
    db_file_path = tmp_path / "scim-client.db"
    db_connection_string = f"sqlite:///{db_file_path}"
    monkeypatch.setenv("PROVISIONING_DB", db_connection_string)

    database = DBSession(db_connection_string)
    initialize_db(database)

    yield database

    database.engine.dispose()
    db_file_path.unlink(missing_ok=True)


def pytest_addoption(parser):
    parser.addoption("--randomly-seed", help="Seed to use for Faker randomization.")
