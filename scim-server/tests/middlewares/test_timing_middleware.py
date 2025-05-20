# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

import time
from typing import Any
from unittest.mock import patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from loguru import logger

from univention.scim.server.middlewares.timing import add_timing_middleware


@pytest.fixture
def test_app() -> FastAPI:
    """Create a FastAPI app for testing."""
    app = FastAPI()

    @app.get("/test")
    async def test_endpoint() -> dict[str, str]:
        return {"message": "test"}

    @app.get("/slow")
    async def slow_endpoint() -> dict[str, str]:
        time.sleep(0.1)  # simulate a slow endpoint
        return {"message": "slow test"}

    return app


@pytest.fixture
def client(test_app: FastAPI) -> TestClient:
    """Create a test client with the timing middleware."""
    add_timing_middleware(test_app, prefix="TEST ")
    return TestClient(test_app)


def test_timing_middleware_logs_request_time(client: TestClient, caplog: Any) -> None:
    """Test that the timing middleware logs the request time."""
    with patch.object(logger, "info") as mock_logger:
        response = client.get("/test")
        assert response.status_code == 200

        # Check that logger.info was called with timing information
        mock_logger.assert_called_once()
        args, kwargs = mock_logger.call_args

        # Check the log message format
        assert args[0] == "TEST Request timing"

        # Check that required fields are present
        assert "request_path" in kwargs
        assert "request_method" in kwargs
        assert "status_code" in kwargs
        assert "process_time_ms" in kwargs

        # Check the values
        assert kwargs["request_path"] == "/test"
        assert kwargs["request_method"] == "GET"
        assert kwargs["status_code"] == 200
        assert isinstance(kwargs["process_time_ms"], float)


def test_slow_endpoint_takes_longer(client: TestClient) -> None:
    """Test that slower endpoints report longer times."""
    with patch.object(logger, "info") as mock_logger:
        # Call the slow endpoint
        response = client.get("/slow")
        assert response.status_code == 200

        # Get the process time from the log
        _, kwargs = mock_logger.call_args
        slow_time = kwargs["process_time_ms"]

        # Reset the mock
        mock_logger.reset_mock()

        # Call the fast endpoint
        response = client.get("/test")
        assert response.status_code == 200

        # Get the process time from the log
        _, kwargs = mock_logger.call_args
        fast_time = kwargs["process_time_ms"]

        # The slow endpoint should take longer than the fast endpoint
        assert slow_time > fast_time
