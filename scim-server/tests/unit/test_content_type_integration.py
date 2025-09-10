# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH


from fastapi.testclient import TestClient


def test_service_provider_config_with_json_accept(client: TestClient) -> None:
    """Test ServiceProviderConfig endpoint with application/json accept header."""
    response = client.get("/scim/v2/ServiceProviderConfig", headers={"Accept": "application/json"})
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json; charset=utf-8"
    data = response.json()
    assert "schemas" in data


def test_service_provider_config_with_scim_accept(client: TestClient) -> None:
    """Test ServiceProviderConfig endpoint with application/scim+json accept header."""
    response = client.get("/scim/v2/ServiceProviderConfig", headers={"Accept": "application/scim+json"})
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/scim+json; charset=utf-8"
    data = response.json()
    assert "schemas" in data


def test_service_provider_config_with_default_accept(client: TestClient) -> None:
    """Test ServiceProviderConfig endpoint with no specific accept header."""
    response = client.get("/scim/v2/ServiceProviderConfig")
    assert response.status_code == 200
    # Should default to SCIM content type
    assert response.headers["content-type"] == "application/scim+json; charset=utf-8"
    data = response.json()
    assert "schemas" in data


def test_schemas_endpoint_with_json_accept(client: TestClient) -> None:
    """Test Schemas endpoint with application/json accept header."""
    response = client.get("/scim/v2/Schemas", headers={"Accept": "application/json"})
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json; charset=utf-8"
    data = response.json()
    assert "schemas" in data
    assert "Resources" in data


def test_schemas_endpoint_with_scim_accept(client: TestClient) -> None:
    """Test Schemas endpoint with application/scim+json accept header."""
    response = client.get("/scim/v2/Schemas", headers={"Accept": "application/scim+json"})
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/scim+json; charset=utf-8"
    data = response.json()
    assert "schemas" in data
    assert "Resources" in data


def test_resource_types_with_both_accepts(client: TestClient) -> None:
    """Test ResourceTypes endpoint accepts both content types."""
    # Test with application/json
    response_json = client.get("/scim/v2/ResourceTypes", headers={"Accept": "application/json"})
    assert response_json.status_code == 200
    assert response_json.headers["content-type"] == "application/json; charset=utf-8"

    # Test with application/scim+json
    response_scim = client.get("/scim/v2/ResourceTypes", headers={"Accept": "application/scim+json"})
    assert response_scim.status_code == 200
    assert response_scim.headers["content-type"] == "application/scim+json; charset=utf-8"

    # Both should return the same data
    assert response_json.json() == response_scim.json()


def test_mixed_accept_header_preferences(client: TestClient) -> None:
    """Test various combinations of accept headers."""
    test_cases: list[tuple[str, str]] = [
        ("application/json, application/scim+json", "application/scim+json; charset=utf-8"),
        ("application/scim+json, application/json", "application/scim+json; charset=utf-8"),
        ("text/html, application/json", "application/json; charset=utf-8"),
        ("*/*", "application/scim+json; charset=utf-8"),
        ("application/*", "application/scim+json; charset=utf-8"),
    ]

    for accept_header, expected_content_type in test_cases:
        response = client.get("/scim/v2/ServiceProviderConfig", headers={"Accept": accept_header})
        assert response.status_code == 200
        assert response.headers["content-type"] == expected_content_type, f"Failed for Accept: {accept_header}"
