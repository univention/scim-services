# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH


from fastapi.testclient import TestClient
from scim2_models import Email, Group, Name, User

from univention.scim.server.config import ApplicationSettings


# Test data
test_user = User(
    user_name="jdoe",
    name=Name(
        given_name="John",
        family_name="Doe",
        formatted="John Doe",
    ),
    password="securepassword",
    active=True,
    emails=[
        Email(
            value="john.doe@example.org",
            type="work",
            primary=True,
        )
    ],
)

test_group = Group(
    display_name="Test Group",
)


class TestUserAPI:
    """Tests for the User endpoints of the SCIM API."""

    def _create_test_user(self, client: TestClient) -> str:
        """Helper method to create a test user and return the ID."""
        response = client.post("/scim/v2/Users", json=test_user.model_dump(by_alias=True, exclude_none=True))
        assert response.status_code == 201
        data = response.json()
        return str(data["id"])

    def test_create_user(self, client: TestClient) -> None:
        """Test creating a user."""
        response = client.post("/scim/v2/Users", json=test_user.model_dump(by_alias=True, exclude_none=True))
        assert response.status_code == 201
        data = response.json()

        # Verify response data
        assert data["userName"] == test_user.user_name
        assert data["name"]["givenName"] == test_user.name.given_name
        assert data["name"]["familyName"] == test_user.name.family_name
        assert "id" in data

    def test_get_user(self, client: TestClient) -> None:
        """Test retrieving a user."""
        # First create a user
        user_id = self._create_test_user(client)

        # Get the user
        response = client.get(f"/scim/v2/Users/{user_id}")
        assert response.status_code == 200
        data = response.json()

        # Verify response data
        assert data["id"] == user_id
        assert data["userName"] == test_user.user_name
        assert data["name"]["givenName"] == test_user.name.given_name
        assert data["name"]["familyName"] == test_user.name.family_name

    def test_list_users(self, client: TestClient) -> None:
        """Test listing users."""
        response = client.get("/scim/v2/Users")
        assert response.status_code == 200
        data = response.json()

        # Verify response structure
        assert "schemas" in data
        assert "urn:ietf:params:scim:api:messages:2.0:ListResponse" in data["schemas"]
        assert "totalResults" in data
        assert "Resources" in data
        assert isinstance(data["Resources"], list)

    def test_update_user(self, client: TestClient) -> None:
        """Test updating a user."""
        # First create a user
        user_id = self._create_test_user(client)

        # Update the user
        updated_user = test_user.model_copy()
        updated_user.name.given_name = "Jane"

        # Do not update the password UDM does not allow setting the same password
        updated_user.password = None

        response = client.put(
            f"/scim/v2/Users/{user_id}", json=updated_user.model_dump(by_alias=True, exclude_none=True)
        )
        assert response.status_code == 200
        data = response.json()

        # Verify response data
        assert data["id"] == user_id
        assert data["userName"] == updated_user.user_name
        assert data["name"]["givenName"] == updated_user.name.given_name
        assert data["name"]["familyName"] == updated_user.name.family_name

    from fastapi.testclient import TestClient

    def test_apply_patch_operations(self, client: TestClient) -> None:
        """Test partially updating a user using PATCH."""
        # Step 1: Create a user
        user_id = self._create_test_user(client)
        user_url = f"/scim/v2/Users/{user_id}"

        # Step 2: Fetch the user before patching
        pre_patch_response = client.get(user_url)
        assert pre_patch_response.status_code == 200, f"Failed to fetch user: {pre_patch_response.text}"
        original_user = pre_patch_response.json()
        # Assert initial state is different
        assert original_user["name"]["givenName"] != "Jane2"
        assert original_user["displayName"] != "Jane2 Smith"

        # Step 3: Prepare SCIM-compliant patch payload
        patch_operations = {
            "Operations": [
                {"op": "replace", "path": "name.givenName", "value": "Jane2"},
                {"op": "replace", "path": "displayName", "value": "Jane2 Smith"},
            ]
        }

        # Step 4: Send PATCH request
        patch_response = client.patch(
            user_url,
            json=patch_operations,
            headers={"Content-Type": "application/json"},
        )

        assert patch_response.status_code == 200, f"PATCH failed: {patch_response.text}"
        data = patch_response.json()

        # Step 5: Verify updated values
        assert data["id"] == user_id
        assert data["name"]["givenName"] == "Jane2"
        assert data["displayName"] == "Jane2 Smith"

        # Step 6: Optionally verify unchanged fields
        assert "familyName" in data["name"]

    def test_patch_nonexistent_user(self, client: TestClient) -> None:
        """PATCHing a non-existent user should return 404 or a handled error."""
        non_existent_id = "non-existent-id-123"
        patch_url = f"/scim/v2/Users/{non_existent_id}"

        patch_operations = {
            "Operations": [
                {"op": "replace", "path": "name.givenName", "value": "Ghost"},
            ]
        }

        response = client.patch(
            patch_url,
            json=patch_operations,
            headers={"Content-Type": "application/json"},
        )

        assert response.status_code in (404, 400), f"Expected failure but got: {response.status_code}"
        assert "not found" in response.text.lower()

    def test_patch_with_invalid_payload(self, client: TestClient) -> None:
        """PATCH with malformed data should be rejected with 400."""
        user_id = self._create_test_user(client)
        user_url = f"/scim/v2/Users/{user_id}"

        pre_patch_response = client.get(user_url)
        assert pre_patch_response.status_code == 200, f"Failed to fetch user: {pre_patch_response.text}"
        original_user = pre_patch_response.json()
        assert original_user["name"]["givenName"] != "Jane2"
        assert original_user["displayName"] != "Jane2 Smith"

        patch_operations = {
            "Operations": [
                {"op": "replace", "path": "bad_field", "value": "oops"},
            ]
        }
        patch_response = client.patch(
            user_url,
            json=patch_operations,
            headers={"Content-Type": "application/json"},
        )

        assert patch_response.status_code == 400
        assert " validation error " in patch_response.text

    def test_patch_with_invalid_payload_broken(self, client: TestClient) -> None:
        """PATCH with malformed data should be rejected with 400."""
        user_id = self._create_test_user(client)
        user_url = f"/scim/v2/Users/{user_id}"

        pre_patch_response = client.get(user_url)
        assert pre_patch_response.status_code == 200, f"Failed to fetch user: {pre_patch_response.text}"
        original_user = pre_patch_response.json()
        assert original_user["name"]["givenName"] != "Jane2"
        assert original_user["displayName"] != "Jane2 Smith"

        invalid_patch = {"bad_field": "oops"}

        patch_response = client.patch(
            user_url,
            json=invalid_patch,
            headers={"Content-Type": "application/json"},
        )

        assert patch_response.status_code == 400
        assert "Operations" in patch_response.text or "Invalid" in patch_response.text

    def test_patch_remove_attribute(self, client: TestClient) -> None:
        """PATCH to remove a user attribute should succeed and result in deletion."""
        user_id = self._create_test_user(client)
        user_url = f"/scim/v2/Users/{user_id}"

        # Confirm field exists before deletion
        user_before = client.get(user_url).json()
        assert "name" in user_before and "givenName" in user_before["name"]

        # Remove the 'givenName' field
        patch_operations = {
            "Operations": [
                {"op": "remove", "path": "name.givenName"},
            ]
        }

        patch_response = client.patch(
            user_url,
            json=patch_operations,
            headers={"Content-Type": "application/json"},
        )

        assert patch_response.status_code == 200
        user_after = patch_response.json()

        # Expect 'givenName' to be gone (or None)
        assert "name" in user_after
        assert "givenName" not in user_after["name"] or user_after["name"]["givenName"] in ("", None)

    def test_patch_add_with_nested_extension_path(self, client: TestClient) -> None:
        """
        PATCH 'add' operation should create missing intermediate
        objects if nested fields are missing and not fail with an exception,
        however, adding some random field should give a 400
        """
        user_id = self._create_test_user(client)
        user_url = f"/scim/v2/Users/{user_id}"

        # Confirm extension is not present initially
        user_before = client.get(user_url).json()
        extension_schema = "unknown_nested_field"
        assert extension_schema not in user_before

        patch_operations = {
            "Operations": [
                {
                    "op": "add",
                    "path": f"{extension_schema}.department",
                    "value": "Engineering",
                }
            ]
        }

        patch_response = client.patch(
            user_url,
            json=patch_operations,
            headers={"Content-Type": "application/json"},
        )

        assert patch_response.status_code == 400

    def test_delete_user(self, client: TestClient) -> None:
        """Test deleting a user."""
        # First create a user
        user_id = self._create_test_user(client)

        # Delete the user
        response = client.delete(f"/scim/v2/Users/{user_id}")
        assert response.status_code == 204

        # Verify the user is deleted
        response = client.get(f"/scim/v2/Users/{user_id}")
        assert response.status_code == 404

    def test_get_nonexistent_user(self, client: TestClient) -> None:
        """Test getting a nonexistent user."""
        response = client.get("/scim/v2/Users/nonexistent")
        assert response.status_code == 404

    def test_update_nonexistent_user(self, client: TestClient) -> None:
        """Test updating a nonexistent user."""
        response = client.put("/scim/v2/Users/nonexistent", json=test_user.model_dump(by_alias=True, exclude_none=True))
        assert response.status_code == 404

    def test_delete_nonexistent_user(self, client: TestClient) -> None:
        """Test deleting a nonexistent user."""
        response = client.delete("/scim/v2/Users/nonexistent")
        assert response.status_code == 404

    def test_filter_users(self, client: TestClient) -> None:
        """Test filtering users."""
        # First create a user
        self.test_create_user(client)

        # Filter users by userName
        response = client.get(f"/scim/v2/Users?filter=userName eq {test_user.user_name}")
        assert response.status_code == 200
        data = response.json()

        # Verify filtered results
        assert data["totalResults"] >= 1
        assert any(u["userName"] == test_user.user_name for u in data["Resources"])


class TestGroupAPI:
    """Tests for the Group endpoints of the SCIM API."""

    def _create_test_group(self, client: TestClient) -> str:
        """Helper method to create a test group and return the ID."""
        response = client.post("/scim/v2/Groups", json=test_group.model_dump(by_alias=True, exclude_none=True))
        assert response.status_code == 201
        data = response.json()
        return str(data["id"])

    def test_create_group(self, client: TestClient) -> None:
        """Test creating a group."""
        response = client.post("/scim/v2/Groups", json=test_group.model_dump(by_alias=True, exclude_none=True))

        assert response.status_code == 201
        data = response.json()

        # Verify response data
        assert data["displayName"] == test_group.display_name
        assert "id" in data

    def test_list_groups(self, client: TestClient) -> None:
        """Test listing groups."""
        response = client.get("/scim/v2/Groups")

        assert response.status_code == 200
        data = response.json()

        # Verify response structure
        assert "schemas" in data
        assert "urn:ietf:params:scim:api:messages:2.0:ListResponse" in data["schemas"]
        assert "totalResults" in data
        assert "Resources" in data
        assert isinstance(data["Resources"], list)

    def test_get_group(self, client: TestClient) -> None:
        """Test retrieving a group."""
        # First create a group
        group_id = self._create_test_group(client)

        # Get the group
        response = client.get(f"/scim/v2/Groups/{group_id}")

        assert response.status_code == 200
        data = response.json()

        # Verify response data
        assert data["id"] == group_id
        assert data["displayName"] == test_group.display_name

    def test_apply_patch_operation(self, client: TestClient) -> None:
        """Test creating a group."""

        group_id = self._create_test_group(client)
        group_url = f"/scim/v2/Groups/{group_id}"

        # Step 2: Fetch the group before patching
        pre_patch_response = client.get(group_url)
        assert pre_patch_response.status_code == 200, f"Failed to fetch group: {pre_patch_response.text}"
        original_group = pre_patch_response.json()
        # Verify response data
        assert original_group["displayName"] == test_group.display_name

        # Step 3: Prepare SCIM-compliant patch payload
        patch_operations = {
            "Operations": [
                {"op": "replace", "path": "displayName", "value": "It's not a cult"},
            ]
        }

        # Step 4: Send PATCH request
        patch_response = client.patch(
            group_url,
            json=patch_operations,
            headers={"Content-Type": "application/json"},
        )

        assert patch_response.status_code == 200, f"PATCH failed: {patch_response.text}"
        data = patch_response.json()

        # Step 5: Verify updated values
        assert data["displayName"] == "It's not a cult"
        assert "id" in data

    def test_patch_nonexistent_group(self, client: TestClient) -> None:
        """PATCHing a non-existent group should return 404 or a handled error."""
        non_existent_id = "non-existent-id-123"
        patch_url = f"/scim/v2/Groups/{non_existent_id}"

        patch_operations = {
            "Operations": [
                {"op": "replace", "path": "displayName", "value": "GhostGroup"},
            ]
        }

        response = client.patch(
            patch_url,
            json=patch_operations,
            headers={"Content-Type": "application/json"},
        )

        assert response.status_code in (404, 400), f"Expected failure but got: {response.status_code}"
        assert "not found" in response.text.lower()

    def test_patch_with_invalid_payload(self, client: TestClient) -> None:
        """PATCH with malformed data should be rejected with 400."""
        group_id = self._create_test_group(client)
        group_url = f"/scim/v2/Groups/{group_id}"

        pre_patch_response = client.get(group_url)
        assert pre_patch_response.status_code == 200, f"Failed to fetch group: {pre_patch_response.text}"
        data = pre_patch_response.json()

        assert data["displayName"] == test_group.display_name

        patch_operations = {
            "Operations": [
                {"op": "replace", "path": "bad_field", "value": "oops"},
            ]
        }
        patch_response = client.patch(
            group_url,
            json=patch_operations,
            headers={"Content-Type": "application/json"},
        )

        assert patch_response.status_code == 400
        assert " validation error " in patch_response.text

    def test_patch_with_invalid_payload_broken(self, client: TestClient) -> None:
        """PATCH with malformed data should be rejected with 400."""
        group_id = self._create_test_group(client)
        group_url = f"/scim/v2/Groups/{group_id}"

        pre_patch_response = client.get(group_url)
        assert pre_patch_response.status_code == 200, f"Failed to fetch group: {pre_patch_response.text}"
        original_group = pre_patch_response.json()
        assert original_group["displayName"] != "Cult group"

        invalid_patch = {"bad_field": "oops"}

        patch_response = client.patch(
            group_url,
            json=invalid_patch,
            headers={"Content-Type": "application/json"},
        )

        assert patch_response.status_code == 400
        assert "Operations" in patch_response.text or "Invalid" in patch_response.text

    def test_patch_remove_attribute(self, client: TestClient) -> None:
        """PATCH to remove a group attribute should succeed and result in deletion."""
        group_id = self._create_test_group(client)
        group_url = f"/scim/v2/Groups/{group_id}"

        # Confirm field exists before deletion
        group_before = client.get(group_url).json()
        assert "displayName" in group_before

        # Remove the 'displayName' field
        patch_operations = {
            "Operations": [
                {"op": "remove", "path": "displayName"},
            ]
        }

        patch_response = client.patch(
            group_url,
            json=patch_operations,
            headers={"Content-Type": "application/json"},
        )

        assert patch_response.status_code == 400  # should retry to remove it but since its not allowed it should fail


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


class TestSchemasEndpoint:
    """Tests for the Schemas endpoint."""

    def test_get_schemas(self, client: TestClient) -> None:
        """Test retrieving the SCIM supported schemas using ListResponse."""
        response = client.get("/scim/v2/Schemas")
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, dict), "Response should be a dictionary (ListResponse)"

        # Validate ListResponse structure
        assert "schemas" in data
        assert "urn:ietf:params:scim:api:messages:2.0:ListResponse" in data["schemas"]
        assert "totalResults" in data
        assert data["totalResults"] >= 3  # User, Group, Common
        assert "Resources" in data
        assert isinstance(data["Resources"], list)

        resources = data["Resources"]

        # Find each expected schema in Resources
        user_schema = next((s for s in resources if s["id"] == "urn:ietf:params:scim:schemas:core:2.0:User"), None)
        group_schema = next((s for s in resources if s["id"] == "urn:ietf:params:scim:schemas:core:2.0:Group"), None)
        common_schema = next((s for s in resources if s["id"] == "urn:ietf:params:scim:schemas:core:2.0:Common"), None)

        # Verify all schemas exist
        assert user_schema is not None, "User schema is missing"
        assert group_schema is not None, "Group schema is missing"
        assert common_schema is not None, "Common schema is missing"

        # Test User schema structure
        assert user_schema["name"] == "User"
        assert user_schema["description"] == "User Account"
        assert isinstance(user_schema["attributes"], list)

        # Check for important User attributes
        user_attributes = {attr["name"] for attr in user_schema["attributes"]}
        assert "username" in user_attributes, "username attribute missing from User schema"
        assert "displayname" in user_attributes, "displayname attribute missing from User schema"

        # Verify attribute properties
        username_attr = next(attr for attr in user_schema["attributes"] if attr["name"] == "username")
        assert username_attr["uniqueness"] == "server"

        # Test Group schema
        assert group_schema["name"] == "Group"
        group_attributes = {attr["name"] for attr in group_schema["attributes"]}
        assert "displayname" in group_attributes
        assert "members" in group_attributes

        # Test Common schema
        common_attributes = {attr["name"] for attr in common_schema["attributes"]}
        expected_common_attrs = {"id", "externalId", "meta", "schemas"}
        for attr in expected_common_attrs:
            assert attr in common_attributes, f"Common schema missing attribute: {attr}"


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
        assert user_type.get("description") == "User Account"
        assert user_type.get("schema") == "urn:ietf:params:scim:schemas:core:2.0:User"
        assert isinstance(user_type.get("meta"), dict)
        assert user_type["meta"].get("resourceType") == "ResourceType"
        assert (
            user_type["meta"].get("location", "")
            == f"{application_settings.host}{application_settings.api_prefix}/ResourceTypes/User"
        )

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
        assert isinstance(group_type.get("meta"), dict)
        assert group_type["meta"].get("resourceType") == "ResourceType"
        assert (
            group_type["meta"].get("location", "")
            == f"{application_settings.host}{application_settings.api_prefix}/ResourceTypes/Group"
        )

        # Check schemaExtensions for Group (should be present and empty)
        assert "schemaExtensions" in group_type
        assert isinstance(group_type["schemaExtensions"], list)
        assert len(group_type["schemaExtensions"]) == 0, "Expected empty schemaExtensions list for Group"
