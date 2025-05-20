# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

from typing import Any
from unittest.mock import patch

import pytest
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient
from lancelog import LogLevel
from loguru import logger

from univention.scim.server.middlewares.request_logging import setup_request_logging_middleware


class MockSettings:
    """Mock settings for testing different log levels."""

    def __init__(self, log_level: LogLevel = LogLevel.DEBUG):
        self.log_level = log_level


@pytest.fixture
def test_app() -> FastAPI:
    """Create a FastAPI app for testing."""
    app = FastAPI()

    @app.get("/test")
    async def test_endpoint() -> dict[str, str]:
        return {"message": "test"}

    @app.post("/users")
    async def create_user(user_data: dict[str, Any]) -> dict[str, str]:
        return {"id": "new-user-id", "status": "created"}

    @app.post("/auth")
    async def auth_endpoint(credentials: dict[str, str]) -> dict[str, str]:
        return {"token": "test-token"}

    @app.get("/error")
    async def error_endpoint() -> JSONResponse:
        return JSONResponse(status_code=404, content={"error": "Not found"})

    @app.get("/long")
    async def long_response() -> dict[str, str]:
        return {"message": "This is a very long message that should be truncated"}

    return app


@pytest.fixture
def client(test_app: FastAPI) -> TestClient:
    """Create a test client with the request logging middleware."""
    with patch(
        "univention.scim.server.middlewares.request_logging.application_settings",
        return_value=MockSettings(LogLevel.DEBUG),
    ):
        setup_request_logging_middleware(test_app)
        return TestClient(test_app)


def test_request_logging_middleware_debug_mode(client: TestClient) -> None:
    """Test that the request logging middleware logs requests and responses in debug mode."""
    with patch.object(logger, "debug") as mock_logger:
        response = client.get("/test")
        assert response.status_code == 200

        # Check that logger.debug was called for both request and response
        assert mock_logger.call_count == 2

        # Check request logging
        request_call_args = mock_logger.call_args_list[0]
        assert request_call_args[0][0] == "SCIM Request"
        request_kwargs = request_call_args[1]
        assert request_kwargs["method"] == "GET"
        assert request_kwargs["path"] == "/test"
        assert "headers" in request_kwargs

        # Check response logging
        response_call_args = mock_logger.call_args_list[1]
        assert response_call_args[0][0] == "SCIM Response"
        response_kwargs = response_call_args[1]
        assert response_kwargs["method"] == "GET"
        assert response_kwargs["path"] == "/test"
        assert response_kwargs["status_code"] == 200
        assert "headers" in response_kwargs


def test_request_logging_middleware_info_mode(client: TestClient) -> None:
    """Test that the request logging middleware doesn't log details in info mode."""
    # Override the client fixture to use INFO log level
    app = FastAPI()

    @app.get("/test")
    async def test_endpoint() -> dict[str, str]:
        return {"message": "test"}

    with patch(
        "univention.scim.server.middlewares.request_logging.application_settings",
        return_value=MockSettings(LogLevel.INFO),
    ):
        setup_request_logging_middleware(app)
        client = TestClient(app)

        with patch.object(logger, "debug") as mock_logger:
            response = client.get("/test")
            assert response.status_code == 200

            # Verify that debug logging was not called
            assert mock_logger.call_count == 0


def test_request_with_json_body(client: TestClient) -> None:
    """Test logging of requests with JSON body."""
    with patch.object(logger, "debug") as mock_logger:
        user_data = {"username": "testuser", "email": "test@example.com", "password": "secret123"}

        response = client.post("/users", json=user_data)
        assert response.status_code == 200

        # Check request logging
        request_call_args = mock_logger.call_args_list[0]
        request_kwargs = request_call_args[1]

        # Verify body is logged with password redacted
        assert "body" in request_kwargs
        assert request_kwargs["body"]["username"] == "testuser"
        assert request_kwargs["body"]["email"] == "test@example.com"
        assert request_kwargs["body"]["password"] == "[REDACTED]"


def test_auth_request_header_redaction(client: TestClient) -> None:
    """Test that authorization headers are properly redacted."""
    with patch.object(logger, "debug") as mock_logger:
        headers = {"Authorization": "Bearer secret-token-123"}
        response = client.get("/test", headers=headers)
        assert response.status_code == 200

        # Check request logging
        request_call_args = mock_logger.call_args_list[0]
        request_kwargs = request_call_args[1]

        # Verify authorization header is redacted
        assert "headers" in request_kwargs
        assert request_kwargs["headers"]["authorization"] == "[REDACTED]"


def test_non_json_body_handling(client: TestClient) -> None:
    """Test logging of requests with non-JSON body."""
    with patch.object(logger, "debug") as mock_logger:
        # Send a request with non-JSON body
        data = "This is a plain text body"
        headers = {"Content-Type": "text/plain"}

        # Use data as bytes to avoid type error
        client.post("/users", content=data.encode("utf-8"), headers=headers)

        # Check request logging
        request_call_args = mock_logger.call_args_list[0]
        request_kwargs = request_call_args[1]

        # Verify body is logged as text
        assert "body" in request_kwargs
        assert request_kwargs["body"] == "This is a plain text body"


def test_query_params_logging(client: TestClient) -> None:
    """Test that query parameters are properly logged."""
    with patch.object(logger, "debug") as mock_logger:
        response = client.get("/test?param1=value1&param2=value2")
        assert response.status_code == 200

        # Check request logging
        request_call_args = mock_logger.call_args_list[0]
        request_kwargs = request_call_args[1]

        # Verify query parameters are logged
        assert "query_params" in request_kwargs
        assert request_kwargs["query_params"] == {"param1": "value1", "param2": "value2"}


def test_body_reading_error_handling(client: TestClient) -> None:
    """Test handling of errors when reading request body."""
    with (
        patch.object(logger, "debug") as mock_logger,
        patch("fastapi.Request.body", side_effect=Exception("Test error")),
    ):
        client.post("/users", json={"test": "data"})

        # Check request logging
        request_call_args = mock_logger.call_args_list[0]
        request_kwargs = request_call_args[1]

        # Verify error is logged
        assert "body_error" in request_kwargs
        assert "Test error" in request_kwargs["body_error"]
