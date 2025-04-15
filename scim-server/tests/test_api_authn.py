# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

from typing import Any
from unittest.mock import MagicMock

import pytest
from _pytest.logging import LogCaptureFixture
from fastapi import HTTPException
from fastapi.testclient import TestClient
from loguru import logger

from univention.scim.server.authn.authn import Authentication
from univention.scim.server.authn.fast_api_adapter import FastAPIAuthAdapter
from univention.scim.server.config import ApplicationSettings
from univention.scim.server.container import ApplicationContainer
from univention.scim.server.main import app


@pytest.fixture
def authenticator_mock() -> Authentication:
    mock = MagicMock(spec=Authentication)

    with ApplicationContainer.authenticator.override(mock):
        yield mock


@pytest.fixture
def disable_authentication(application_settings: ApplicationSettings) -> ApplicationSettings:
    application_settings.auth_enabled = False
    return application_settings


@pytest.mark.usefixtures("disable_authentication")
def test_auth_disabled(authenticator_mock: Authentication, client: TestClient) -> None:
    authenticator_mock.authenticate.side_effect = HTTPException(status_code=403, detail="Auth error in test.")

    response = client.get("/scim/v2/Users")
    assert response.status_code == 200
    assert authenticator_mock.authenticate.call_count == 0


def test_auth_fail(client: TestClient) -> None:
    class FastAPIAuthAdapterMock:
        def __call__(self) -> None:
            raise HTTPException(status_code=403, detail="Auth error in test.")

    app.dependency_overrides[FastAPIAuthAdapter] = FastAPIAuthAdapterMock()

    response = client.get("/scim/v2/Users")
    app.dependency_overrides = {}

    assert response.status_code == 403, repr(response.__dict__)


def test_auth_success(client: TestClient, caplog: LogCaptureFixture) -> None:
    msg = "Mock 007"

    class FastAPIAuthAdapterMock:
        def __call__(self) -> dict[str, Any]:
            logger.info(msg)
            return {"username": "admin", "roles": ["admin"]}

    app.dependency_overrides[FastAPIAuthAdapter] = FastAPIAuthAdapterMock()

    response = client.get("/scim/v2/Users")
    app.dependency_overrides = {}

    assert response.status_code == 200, repr(response.__dict__)
    assert msg in caplog.messages
