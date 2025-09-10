# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

from typing import Any

import pytest
from fastapi import FastAPI, Response
from fastapi.testclient import TestClient

from univention.scim.server.middlewares.content_type import add_content_type_middleware


@pytest.fixture
def app() -> FastAPI:
    """Create a test FastAPI app with the content type middleware."""
    app = FastAPI()
    add_content_type_middleware(app)

    @app.get("/test")
    async def test_endpoint() -> dict[str, str]:
        return {"message": "test"}

    @app.post("/test")
    async def test_post_endpoint(data: dict[str, Any]) -> dict[str, Any]:
        return {"received": data}

    @app.get("/test-html")
    async def test_html_endpoint() -> Response:
        return Response(content="<html><body>Test</body></html>", media_type="text/html")

    return app


@pytest.fixture
def client(app: FastAPI) -> TestClient:
    """Create a test client."""
    return TestClient(app)


def test_default_response_content_type_is_scim(client: TestClient) -> None:
    """Test that default response content type is application/scim+json."""
    response = client.get("/test")
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/scim+json; charset=utf-8"


def test_response_content_type_with_scim_accept_header(client: TestClient) -> None:
    """Test response content type when client accepts SCIM."""
    response = client.get("/test", headers={"Accept": "application/scim+json"})
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/scim+json; charset=utf-8"


def test_response_content_type_with_json_accept_header(client: TestClient) -> None:
    """Test response content type when client only accepts JSON."""
    response = client.get("/test", headers={"Accept": "application/json"})
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json; charset=utf-8"


def test_response_content_type_with_both_accept_headers(client: TestClient) -> None:
    """Test response content type when client accepts both JSON and SCIM."""
    response = client.get("/test", headers={"Accept": "application/json, application/scim+json"})
    assert response.status_code == 200
    # When both are accepted, should default to SCIM
    assert response.headers["content-type"] == "application/scim+json; charset=utf-8"


def test_non_json_response_unchanged(client: TestClient) -> None:
    """Test that non-JSON responses are not affected by the middleware."""
    response = client.get("/test-html")
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/html; charset=utf-8"


def test_accepts_application_json_content_type(client: TestClient) -> None:
    """Test that server accepts application/json content type for requests."""
    data = {"test": "value"}
    response = client.post("/test", json=data, headers={"Content-Type": "application/json"})
    assert response.status_code == 200
    assert response.json()["received"] == data


def test_accepts_application_scim_json_content_type(client: TestClient) -> None:
    """Test that server accepts application/scim+json content type for requests."""
    data = {"test": "value"}
    response = client.post("/test", json=data, headers={"Content-Type": "application/scim+json"})
    assert response.status_code == 200
    assert response.json()["received"] == data


def test_request_with_scim_content_type_and_json_accept(client: TestClient) -> None:
    """Test request with SCIM content type but JSON accept header."""
    data = {"test": "value"}
    response = client.post(
        "/test", json=data, headers={"Content-Type": "application/scim+json", "Accept": "application/json"}
    )
    assert response.status_code == 200
    assert response.json()["received"] == data
    assert response.headers["content-type"] == "application/json; charset=utf-8"


def test_request_with_json_content_type_and_scim_accept(client: TestClient) -> None:
    """Test request with JSON content type but SCIM accept header."""
    data = {"test": "value"}
    response = client.post(
        "/test", json=data, headers={"Content-Type": "application/json", "Accept": "application/scim+json"}
    )
    assert response.status_code == 200
    assert response.json()["received"] == data
    assert response.headers["content-type"] == "application/scim+json; charset=utf-8"
