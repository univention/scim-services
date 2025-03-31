# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from univention.scim.server.authn.authn import Authentication


@pytest.fixture
def authenticator_mock() -> Authentication:
    mock = MagicMock(spec=Authentication)

    from univention.scim.server.container import ApplicationContainer

    with ApplicationContainer.authenticator.override(mock):
        yield mock


def test_auth_fail(authenticator_mock: Authentication, client: TestClient) -> None:
    authenticator_mock.authenticate.side_effect = HTTPException(status_code=403, detail="Auth error in test.")

    response = client.get("/scim/v2/Users")
    assert response.status_code == 403


def test_auth_success(authenticator_mock: Authentication, client: TestClient) -> None:
    authenticator_mock.authenticate.return_value = {"username": "admin", "roles": ["admin"]}

    response = client.get("/scim/v2/Users")
    assert response.status_code == 200
