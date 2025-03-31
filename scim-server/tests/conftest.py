# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

import os
from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from univention.scim.server.config import ApplicationSettings
from dependency_injector.providers import Singleton


@pytest.fixture(autouse=True)
def application_settings(monkeypatch) -> ApplicationSettings:  #  type: ignore
    env = {
        "TOKEN_VALIDATION_ENDPOINT": os.environ.get("TOKEN_VALIDATION_ENDPOINT", "test"),
    }
    for k, v in env.items():
        monkeypatch.setenv(k, v)

    from univention.scim.server.config import application_settings as _application_settings

    yield _application_settings()


@pytest.fixture(autouse=True)
def allow_all_bearer(application_settings: ApplicationSettings) -> Generator[None, None, None]:
    from univention.scim.server.container import ApplicationContainer
    from univention.scim.server.authn.authn_impl import AllowAllBearerAuthentication

    # Make sure that for tests we allow all bearer, auth tests can override it again
    with ApplicationContainer.authenticator.override(AllowAllBearerAuthentication() ):
        yield

@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    # Initialization ApplicationContainer after our overrides are done
    from univention.scim.server.main import app

    with TestClient(app, headers={"Authorization": "Bearer let-me-in"}) as client:
        yield client
