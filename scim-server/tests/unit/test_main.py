# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

from fastapi.testclient import TestClient


def test_main_read_openapi_html(client: TestClient) -> None:
    response = client.get("/docs")
    assert response.status_code == 200
    assert "Univention SCIM Server - Swagger UI" in response.text, repr(response.__dict__)


def test_main_read_openapi_json(client: TestClient) -> None:
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
