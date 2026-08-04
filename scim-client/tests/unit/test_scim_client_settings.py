# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

import httpx
import pytest

from univention.scim.client.scim_client_settings import get_scim_consumer_settings


def test_get_scim_consumer_settings_populates_auth(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SCIM_SERVER_BASE_URL", "http://example.com/scim/v2")
    monkeypatch.setenv("SCIM_AUTH_METHOD", "basic")
    monkeypatch.setenv("SCIM_BASIC_AUTH_USERNAME", "user")
    monkeypatch.setenv("SCIM_BASIC_AUTH_PASSWORD", "pass")

    settings = get_scim_consumer_settings()

    assert isinstance(settings.auth, httpx.BasicAuth)
