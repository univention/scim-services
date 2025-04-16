# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH
import os
from collections.abc import Generator
from typing import TypeVar

import pytest
from _pytest.logging import LogCaptureFixture
from fastapi.testclient import TestClient
from loguru import logger
from scim2_models import Resource

from helpers.allow_all_authn import AllowAllBearerAuthentication, OpenIDConnectConfigurationMock
from univention.scim.server.config import ApplicationSettings
from univention.scim.server.container import ApplicationContainer
from univention.scim.server.main import app


T = TypeVar("T", bound=Resource)


@pytest.fixture(autouse=True)
def application_settings(monkeypatch: pytest.MonkeyPatch) -> Generator[ApplicationSettings, None, None]:
    env = {
        "IDP_OPENID_CONFIGURATION_URL": os.environ.get("IDP_OPENID_CONFIGURATION_URL", "test"),
        "UDM_URL": os.environ.get("UDM_URL", "http://localhost:9979/univention/udm"),
        "UDM_USERNAME": os.environ.get("UDM_USERNAME", "admin"),
        "UDM_PASSWORD": os.environ.get("UDM_PASSWORD", "secret"),
    }
    for k, v in env.items():
        monkeypatch.setenv(k, v)
    # Don't use the application_settings function because we don't want caching for unit tests
    yield ApplicationSettings()


@pytest.fixture(autouse=True)
def allow_all_bearer(application_settings: ApplicationSettings) -> Generator[None, None, None]:
    # Make sure that for tests we allow all bearer
    with (
        ApplicationContainer.authenticator.override(AllowAllBearerAuthentication()),
        ApplicationContainer.oidc_configuration.override(OpenIDConnectConfigurationMock()),
        ApplicationContainer.settings.override(application_settings),
        ApplicationContainer.user_repo.override(user_crud_manager),
        ApplicationContainer.group_repo.override(group_crud_manager),
        ApplicationContainer.user_service.override(user_service),
        ApplicationContainer.group_service.override(group_service),
    ):
        yield


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    with TestClient(app, headers={"Authorization": "Bearer let-me-in"}) as client:
        yield client

    # remove routes to make sure they are re-added when reusing
    # global app object with updated parameters like disabled authentication
    app.router.routes = []

    # setup OpenAPI routes again
    app.setup()


@pytest.fixture
def caplog(caplog: LogCaptureFixture) -> Generator[LogCaptureFixture, None, None]:
    handler_id = logger.add(
        caplog.handler,
        format="{message}",
        level=0,
        filter=lambda record: record["level"].no >= caplog.handler.level,
        enqueue=False,  # Set to 'True' if your test is spawning child processes.
    )
    yield caplog
    logger.remove(handler_id)
