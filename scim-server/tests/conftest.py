# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

import os
from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="session", autouse=True)
def application_settings():  # type: ignore
    env = {
        "TOKEN_VALIDATION_ENDPOINT": os.environ.get("TOKEN_VALIDATION_ENDPOINT", "test"),
    }
    for k, v in env.items():
        os.environ[k] = v

    from univention.scim.server.config import application_settings as _application_settings

    yield _application_settings()


@pytest.fixture  # type: ignore
def client() -> Generator[TestClient, None, None]:
    from univention.scim.server.container import ApplicationContainer
    from univention.scim.server.authn.authn_impl import AllowAllBearerAuthentication
    from univention.scim.server.main import app

    # Make sure that for tests we allow all bearer, auth tests can override it again
    with ApplicationContainer.authenticator.override(AllowAllBearerAuthentication() ):
        with TestClient(app, headers={"Authorization": "Bearer let-me-in"}) as client:
            yield client
