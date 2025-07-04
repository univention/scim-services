# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

from collections.abc import Callable, Generator
from contextlib import _GeneratorContextManager, contextmanager
from typing import Any

import pytest
from fastapi.testclient import TestClient
from scim2_client.engines.httpx import SyncSCIMClient

from univention.scim.server.config import ApplicationSettings


class TestDocuEnabled:
    @pytest.fixture
    def after_setup(
        self, application_settings: ApplicationSettings
    ) -> Callable[[], _GeneratorContextManager[Any, None, None]]:
        @contextmanager
        def enable_docu() -> Generator[None, None, None]:
            application_settings.docu.enabled = True
            yield

        return enable_docu

    def test_main_read_openapi_html(self, client: TestClient) -> None:
        response = client.get("/docs")
        assert response.status_code == 200
        assert "Univention SCIM Server - Swagger UI" in response.text, repr(response.__dict__)

        response = client.get("/redoc")
        assert response.status_code == 200

    def test_main_read_openapi_json(self, client: TestClient) -> None:
        response = client.get("/openapi.json")
        assert response.status_code == 200
        schema = response.json()
        assert "openapi" in schema
        assert schema.get("info", {}).get("title") == "Univention SCIM Server"
        paths = schema.get("paths", {})
        assert "/scim/v2/Users" in paths
        assert "/scim/v2/Users/{user_id}" in paths
        assert "/scim/v2/Groups" in paths
        assert "/scim/v2/Groups/{group_id}" in paths
        assert "/scim/v2/ServiceProviderConfig" in paths


def test_main_docu_disabled(client: TestClient) -> None:
    response = client.get("/docs")
    assert response.status_code == 404

    response = client.get("/redoc")
    assert response.status_code == 404


def test_discovery_with_scim_client(client: TestClient, api_prefix: str) -> None:
    client.base_url = client.base_url.copy_with(path=api_prefix)
    scim = SyncSCIMClient(client=client)
    scim.discover()
