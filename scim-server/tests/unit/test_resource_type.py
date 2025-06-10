# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

from fastapi.testclient import TestClient

from univention.scim.server.config import ApplicationSettings


class TestResourceTypesEndpoint:
    """Tests for the ResourceTypes endpoint."""

    def test_get_resource_types(self, client: TestClient, application_settings: ApplicationSettings) -> None:
        """Test retrieving the SCIM ResourceTypes in ListResponse format."""
        response = client.get("/scim/v2/ResourceTypes")

        # --- Basic Response Validation ---
        assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
        data = response.json()
        assert isinstance(data, dict), f"Expected response data to be a dict, got {type(data)}"

        # --- ListResponse Structure Validation ---
        assert "schemas" in data, "Response missing 'schemas' field"
        assert isinstance(data["schemas"], list), "'schemas' field should be a list"
        assert "urn:ietf:params:scim:api:messages:2.0:ListResponse" in data["schemas"], (
            "ListResponse schema missing from 'schemas'"
        )

        assert "totalResults" in data, "Response missing 'totalResults' field"
        assert isinstance(data["totalResults"], int), "'totalResults' should be an integer"
        assert data["totalResults"] == 2, (
            f"Expected totalResults 2, got {data['totalResults']}"
        )  # Expecting User and Group

        assert "itemsPerPage" in data, "Response missing 'itemsPerPage' field"
        assert isinstance(data["itemsPerPage"], int), "'itemsPerPage' should be an integer"

        assert "startIndex" in data, "Response missing 'startIndex' field"
        assert isinstance(data["startIndex"], int), "'startIndex' should be an integer"

        assert "Resources" in data, "Response missing 'Resources' field"
        assert isinstance(data["Resources"], list), "'Resources' field should be a list"

        # --- Content Validation (Resources List) ---
        resources_list = data["Resources"]
        assert len(resources_list) == data["totalResults"], (
            f"Number of items in 'Resources' ({len(resources_list)}) does not match "
            "'totalResults' ({data['totalResults']})"
        )

        # Find User and Group within the Resources list
        user_type = next((r for r in resources_list if isinstance(r, dict) and r.get("id") == "User"), None)
        group_type = next((r for r in resources_list if isinstance(r, dict) and r.get("id") == "Group"), None)

        # --- User ResourceType checks ---
        assert user_type is not None, "User ResourceType missing from 'Resources'"
        assert "urn:ietf:params:scim:schemas:core:2.0:ResourceType" in user_type.get("schemas", [])
        assert user_type.get("name") == "User"
        assert user_type.get("endpoint") == "/Users"
        assert user_type.get("description") == "User"
        assert user_type.get("schema") == "urn:ietf:params:scim:schemas:core:2.0:User"

        # Check schemaExtensions for User
        assert "schemaExtensions" in user_type
        assert isinstance(user_type["schemaExtensions"], list)
        assert len(user_type["schemaExtensions"]) == 1, "Expected 1 schemaExtension for User"
        enterprise_ext = user_type["schemaExtensions"][0]
        assert isinstance(enterprise_ext, dict)
        assert enterprise_ext.get("schema") == "urn:ietf:params:scim:schemas:extension:enterprise:2.0:User"
        assert enterprise_ext.get("required") is False

        # --- Group ResourceType checks ---
        assert group_type is not None, "Group ResourceType missing from 'Resources'"
        assert "urn:ietf:params:scim:schemas:core:2.0:ResourceType" in group_type.get("schemas", [])
        assert group_type.get("name") == "Group"
        assert group_type.get("endpoint") == "/Groups"
        assert group_type.get("description") == "Group"
        assert group_type.get("schema") == "urn:ietf:params:scim:schemas:core:2.0:Group"

        # Check schemaExtensions for Group (should be present and empty)
        assert "schemaExtensions" in group_type
        assert isinstance(group_type["schemaExtensions"], list)
        assert len(group_type["schemaExtensions"]) == 0, "Expected empty schemaExtensions list for Group"
