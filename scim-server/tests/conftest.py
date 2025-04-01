# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

import os
from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from univention.scim.server.config import ApplicationSettings, AuthenticatorConfig
from univention.scim.server.main import create_app


@pytest.fixture(autouse=True)
def application_settings(monkeypatch) -> ApplicationSettings:  #  type: ignore
    env = {
        "TOKEN_VALIDATION_ENDPOINT": os.environ.get("TOKEN_VALIDATION_ENDPOINT", "test"),
    }
    for k, v in env.items():
        monkeypatch.setenv(k, v)

    # Don't use the application_settings function because we don't want caching for unit tests
    authenticator = AuthenticatorConfig()
    yield ApplicationSettings(authenticator=authenticator)


@pytest.fixture(autouse=True)
def allow_all_bearer(application_settings: ApplicationSettings) -> Generator[None, None, None]:
    from univention.scim.server.authn.authn_impl import AllowAllBearerAuthentication
    from univention.scim.server.container import ApplicationContainer

    # Make sure that for tests we allow all bearer
    with (
        ApplicationContainer.authenticator.override(AllowAllBearerAuthentication()),
        ApplicationContainer.settings.override(application_settings),
    ):
        yield


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    with TestClient(create_app(), headers={"Authorization": "Bearer let-me-in"}) as client:
        yield client
