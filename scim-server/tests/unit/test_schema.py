# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH
from fastapi.testclient import TestClient


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
        enterprise_user_schema = next(
            (s for s in resources if s["id"] == "urn:ietf:params:scim:schemas:extension:enterprise:2.0:User"), None
        )
        univention_user_schema = next(
            (s for s in resources if s["id"] == "urn:ietf:params:scim:schemas:extension:Univention:1.0:User"), None
        )
        univention_group_schema = next(
            (s for s in resources if s["id"] == "urn:ietf:params:scim:schemas:extension:Univention:1.0:Group"), None
        )
        customer1_user_schema = next(
            (s for s in resources if s["id"] == "urn:ietf:params:scim:schemas:extension:DapUser:2.0:User"), None
        )

        # Verify all schemas exist
        assert user_schema is not None, "User schema is missing"
        assert group_schema is not None, "Group schema is missing"
        assert enterprise_user_schema is not None, "Enterprise user schema is missing"
        assert univention_user_schema is not None, "Univention user schema is missing"
        assert univention_group_schema is not None, "Univention group schema is missing"
        assert customer1_user_schema is not None, "Customer1 user schema is missing"

        # Test User schema structure
        assert user_schema["name"] == "User"
        assert user_schema["description"] == "User"
        assert isinstance(user_schema["attributes"], list)

        # Check for important User attributes
        user_attributes = {attr["name"] for attr in user_schema["attributes"]}
        assert "userName" in user_attributes, "userName attribute missing from User schema"
        assert "displayName" in user_attributes, "displayName attribute missing from User schema"

        # Verify attribute properties
        username_attr = next(attr for attr in user_schema["attributes"] if attr["name"] == "userName")
        assert username_attr["uniqueness"] == "server"

        # Test Group schema
        assert group_schema["name"] == "Group"
        group_attributes = {attr["name"] for attr in group_schema["attributes"]}
        assert "displayName" in group_attributes, "displayName attribute missing from Group schema"
        assert "members" in group_attributes, "members attribute missing from Group schema"

        # Test Enterprise user schema
        assert enterprise_user_schema["name"] == "EnterpriseUser"
        enterprise_user_attributes = {attr["name"] for attr in enterprise_user_schema["attributes"]}
        assert "employeeNumber" in enterprise_user_attributes, (
            "employeeNumber attribute missing from {enterprise_user_schema['name']} schema"
        )

        # Test Univention user schema
        assert univention_user_schema["name"] == "UniventionUser"
        univention_user_attributes = {attr["name"] for attr in univention_user_schema["attributes"]}
        assert "description" in univention_user_attributes, (
            "description attribute missing from {univention_user_schema['name']} schema"
        )
        assert "passwordRecoveryEmail" in univention_user_attributes, (
            "passwordRecoveryEmail attribute missing from {univention_user_schema['name']} schema"
        )

        # Test univention group schema
        assert univention_group_schema["name"] == "UniventionGroup"
        univention_group_attributes = {attr["name"] for attr in univention_group_schema["attributes"]}
        assert "description" in univention_group_attributes, (
            f"description attribute missing from {univention_group_schema['name']} schema"
        )
        assert "memberRoles" in univention_group_attributes, (
            f"memberRoles attribute missing from {univention_group_schema['name']} schema"
        )

        # Test Customer1 user schema
        assert customer1_user_schema["name"] == "Customer1User"
        customer1_user_attributes = {attr["name"] for attr in customer1_user_schema["attributes"]}
        assert "primaryOrgUnit" in customer1_user_attributes, (
            f"primaryOrgUnit attribute missing from {customer1_user_schema['name']} schema"
        )
        assert "secondaryOrgUnits" in customer1_user_attributes, (
            f"secondaryOrgUnits attribute missing from {customer1_user_schema['name']} schema"
        )

    def test_get_schema_by_id(self, client: TestClient) -> None:
        """Test retrieving a SCIM schema by ID."""
        response = client.get("/scim/v2/Schemas/urn:ietf:params:scim:schemas:core:2.0:User")
        assert response.status_code == 200
        user_schema = response.json()

        # Test User schema structure
        assert user_schema["name"] == "User"
        assert user_schema["description"] == "User"
        assert isinstance(user_schema["attributes"], list)

        # Check for important User attributes
        user_attributes = {attr["name"] for attr in user_schema["attributes"]}
        assert "userName" in user_attributes, "userName attribute missing from User schema"
        assert "displayName" in user_attributes, "displayName attribute missing from User schema"
