from fastapi.testclient import TestClient

class TestServiceProviderConfig:
    """Tests for the ServiceProviderConfig endpoint."""

    def test_get_service_provider_config(self, client: TestClient) -> None:
        """Test retrieving the service provider configuration."""
        response = client.get("/scim/v2/ServiceProviderConfig")
        assert response.status_code == 200
        data = response.json()

        # Verify required fields and values
        assert data["schemas"] == ["urn:ietf:params:scim:schemas:core:2.0:ServiceProviderConfig"]

        assert data["patch"]["supported"] is True
        assert data["bulk"]["supported"] is False
        assert data["filter"]["supported"] is True
        assert data["filter"]["maxResults"] == 100  # Note: we currently return 100
        assert data["changePassword"]["supported"] is True
        assert data["sort"]["supported"] is False
        assert data["etag"]["supported"] is False

        # Validate authentication schemes
        auth_schemes = data["authenticationSchemes"]
        assert isinstance(auth_schemes, list)
        assert len(auth_schemes) == 1

        scheme = auth_schemes[0]
        assert scheme["type"] == "oauthbearertoken"
        assert scheme["name"] == "OAuth Bearer Token"
        assert scheme["description"] == "Authentication scheme using the OAuth Bearer Token Standard"
        assert scheme["specUri"] == "http://www.rfc-editor.org/info/rfc6750"
        assert scheme["documentationUri"] == "https://docs.univention.de/scim-api/auth/oauth.html"
        assert scheme["primary"] is True


