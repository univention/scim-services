# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

from collections.abc import Callable, Generator
from contextlib import _GeneratorContextManager, contextmanager
from typing import Any
from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from univention.scim.server.authn.authn import Authentication
from univention.scim.server.config import ApplicationSettings
from univention.scim.server.container import ApplicationContainer


@pytest.fixture
def authenticator_mock() -> Authentication:
    mock = MagicMock(spec=Authentication)

    with ApplicationContainer.authenticator.override(mock):
        yield mock


# Override after_setup tets fixture to inject our override
@pytest.fixture
def after_setup(authenticator_mock: Authentication) -> Callable[[], _GeneratorContextManager[Any, None, None]]:
    @contextmanager
    def override_authenticator() -> Generator[None, None, None]:
        with ApplicationContainer.authenticator.override(authenticator_mock):
            yield

    return override_authenticator


@pytest.fixture
def disable_authentication(application_settings: ApplicationSettings) -> ApplicationSettings:
    application_settings.auth_enabled = False
    return application_settings


@pytest.mark.usefixtures("disable_authentication")
def test_auth_disabled(
    after_setup: Callable[[], _GeneratorContextManager[Any, None, None]],
    authenticator_mock: Authentication,
    client: TestClient,
) -> None:
    authenticator_mock.authenticate.side_effect = HTTPException(status_code=403, detail="Auth error in test.")

    response = client.get("/scim/v2/Users")
    assert response.status_code == 200
    assert authenticator_mock.authenticate.call_count == 0


def test_auth_fail(
    after_setup: Callable[[], _GeneratorContextManager[Any, None, None]],
    authenticator_mock: Authentication,
    client: TestClient,
) -> None:
    authenticator_mock.authenticate.side_effect = HTTPException(status_code=403, detail="Auth error in test.")

    response = client.get("/scim/v2/Users")
    assert response.status_code == 403, repr(response.__dict__)
    assert authenticator_mock.authenticate.call_count == 1


def test_auth_success(
    after_setup: Callable[[], _GeneratorContextManager[Any, None, None]],
    authenticator_mock: Authentication,
    client: TestClient,
) -> None:
    authenticator_mock.authenticate.returns = {"username": "admin", "roles": ["admin"]}

    response = client.get("/scim/v2/Users")
    assert response.status_code == 200, repr(response.__dict__)
    assert authenticator_mock.authenticate.call_count == 1
