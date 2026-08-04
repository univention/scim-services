# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from univention.scim.client.scim_client_settings import ScimConsumerSettings
from univention.scim.client.scim_http_client import ScimClient


@pytest.fixture
def settings() -> ScimConsumerSettings:
    """Create test settings."""
    return ScimConsumerSettings(
        scim_server_base_url="https://example.com/scim/v2",
        scim_auth_method="none",
        health_check_enabled=False,
    )


def test_scim_client_uses_correct_content_type_headers(settings: ScimConsumerSettings) -> None:
    """Test that SCIM client sets proper content type headers."""
    # Mock the SyncSCIMClient and its methods
    with patch("univention.scim.client.scim_http_client.SyncSCIMClient") as mock_scim_client:
        mock_instance = MagicMock()
        mock_instance.get_resource_model.return_value = MagicMock()  # Mock User and Group models
        mock_scim_client.return_value = mock_instance

        # Mock the httpx.Client
        with patch("univention.scim.client.scim_http_client.Client") as mock_client:
            mock_client_instance = MagicMock()
            mock_client.return_value = mock_client_instance

            # Create the SCIM client
            scim_client = ScimClient(auth=None, settings=settings)

            # Trigger client creation
            scim_client._create_client()

            # Verify that the httpx.Client was created with proper headers
            mock_client.assert_called_once()
            call_kwargs: dict[str, Any] = mock_client.call_args[1]

            assert "headers" in call_kwargs
            headers = call_kwargs["headers"]
            assert headers["Accept"] == "application/scim+json"
            assert headers["Content-Type"] == "application/scim+json"


@pytest.mark.parametrize("auth_method", ["oidc", "basic", "bearer"])
def test_scim_client_preserves_auth_for_any_configured_method(auth_method: str) -> None:
    """Test that SCIM client passes through whatever auth object it is given, regardless of method."""
    settings_with_auth = ScimConsumerSettings(
        scim_server_base_url="https://example.com/scim/v2",
        scim_auth_method=auth_method,
        health_check_enabled=False,
    )
    mock_auth = MagicMock()

    with patch("univention.scim.client.scim_http_client.SyncSCIMClient") as mock_scim_client:
        mock_instance = MagicMock()
        mock_instance.get_resource_model.return_value = MagicMock()
        mock_scim_client.return_value = mock_instance

        with patch("univention.scim.client.scim_http_client.Client") as mock_client:
            mock_client_instance = MagicMock()
            mock_client.return_value = mock_client_instance

            scim_client = ScimClient(auth=mock_auth, settings=settings_with_auth)
            scim_client._create_client()

            mock_client.assert_called_once()
            call_kwargs: dict[str, Any] = mock_client.call_args[1]

            assert call_kwargs["auth"] == mock_auth
            assert str(call_kwargs["base_url"]) == settings_with_auth.scim_server_base_url
            assert call_kwargs["headers"]["Accept"] == "application/scim+json"
            assert call_kwargs["headers"]["Content-Type"] == "application/scim+json"


def test_scim_client_no_auth_when_method_is_none(settings: ScimConsumerSettings) -> None:
    """Test that SCIM client makes unauthenticated requests when no auth object is passed in."""
    with patch("univention.scim.client.scim_http_client.SyncSCIMClient") as mock_scim_client:
        mock_instance = MagicMock()
        mock_instance.get_resource_model.return_value = MagicMock()
        mock_scim_client.return_value = mock_instance

        with patch("univention.scim.client.scim_http_client.Client") as mock_client:
            mock_client_instance = MagicMock()
            mock_client.return_value = mock_client_instance

            scim_client = ScimClient(auth=None, settings=settings)
            scim_client._create_client()

            mock_client.assert_called_once()
            call_kwargs: dict[str, Any] = mock_client.call_args[1]

            assert call_kwargs["auth"] is None
            assert str(call_kwargs["base_url"]) == settings.scim_server_base_url
            assert call_kwargs["headers"]["Accept"] == "application/scim+json"
            assert call_kwargs["headers"]["Content-Type"] == "application/scim+json"
