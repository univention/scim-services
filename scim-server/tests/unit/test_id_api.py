# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

import urllib.parse

import pytest
from faker import Faker
from fastapi.testclient import TestClient

from tests.conftest import CreateGroupFactory, CreateUserFactory


class TestIdAPI:
    """Tests for the global UUID endpoints of the SCIM API."""

    @pytest.mark.asyncio
    async def test_get_user_by_id(
        self, client: TestClient, create_random_user: CreateUserFactory, create_random_group: CreateGroupFactory
    ) -> None:
        # First create a user and group
        test_user = await create_random_user()
        await create_random_group()

        # Get the resource
        response = client.get(f"/scim/v2/{test_user.id}")
        assert response.status_code == 200
        data = response.json()

        # Verify response data
        assert data["id"] == test_user.id
        assert data["userName"] == test_user.user_name
        assert data["name"]["givenName"] == test_user.name.given_name
        assert data["name"]["familyName"] == test_user.name.family_name

    @pytest.mark.asyncio
    async def test_get_group_by_id(
        self, client: TestClient, create_random_user: CreateUserFactory, create_random_group: CreateGroupFactory
    ) -> None:
        # First create a user and group
        await create_random_user()
        test_group = await create_random_group()

        # Get the resource
        response = client.get(f"/scim/v2/{test_group.id}")

        assert response.status_code == 200
        data = response.json()

        # Verify response data
        assert data["id"] == test_group.id
        assert data["displayName"] == test_group.display_name

    @pytest.mark.asyncio
    async def test_object_not_found(
        self, client: TestClient, create_random_user: CreateUserFactory, create_random_group: CreateGroupFactory
    ) -> None:
        # First create a user and group
        await create_random_user()
        await create_random_group()

        # Get the resource
        fake = Faker()
        response = client.get(f"/scim/v2/{fake.uuid4()}")
        assert response.status_code == 404
        data = response.json()
        assert data["schemas"] == ["urn:ietf:params:scim:api:messages:2.0:Error"]

    @pytest.mark.asyncio
    async def test_get_users_and_groups(
        self, client: TestClient, create_random_user: CreateUserFactory, create_random_group: CreateGroupFactory
    ) -> None:
        # First create a user and group
        test_user = await create_random_user()
        test_group = await create_random_group()

        # Get the resources
        response = client.get("/scim/v2/")

        assert response.status_code == 200
        data = response.json()

        # Verify response data
        assert data["schemas"] == ["urn:ietf:params:scim:api:messages:2.0:ListResponse"]
        assert data["totalResults"] >= 2
        assert len(data["Resources"]) >= 2
        assert any(resource["id"] == test_user.id for resource in data["Resources"])
        assert any(resource["id"] == test_group.id for resource in data["Resources"])

    @pytest.mark.asyncio
    async def test_get_users_and_groups_partly(
        self, client: TestClient, create_random_user: CreateUserFactory, create_random_group: CreateGroupFactory
    ) -> None:
        # First create a user and group
        await create_random_user()
        await create_random_user()
        await create_random_user()
        await create_random_user()
        await create_random_user()

        await create_random_group()
        await create_random_group()
        await create_random_group()
        await create_random_group()
        await create_random_group()

        # Get the resources
        response = client.get("/scim/v2/?start_index=3&count=4")

        assert response.status_code == 200
        data = response.json()

        # Verify response data
        assert data["schemas"] == ["urn:ietf:params:scim:api:messages:2.0:ListResponse"]
        assert data["totalResults"] >= 4
        assert len(data["Resources"]) >= 4
        assert len([resource for resource in data["Resources"] if resource["meta"]["resourceType"] == "User"]) == 3
        assert len([resource for resource in data["Resources"] if resource["meta"]["resourceType"] == "Group"]) == 1

    @pytest.mark.asyncio
    async def test_filter_by_id(
        self, client: TestClient, create_random_user: CreateUserFactory, create_random_group: CreateGroupFactory
    ) -> None:
        # First create a user and group
        test_user = await create_random_user()
        test_group = await create_random_group()

        # Filter users by id
        response = client.get(f"/scim/v2/?filter=id eq {test_user.id}")
        assert response.status_code == 200
        data = response.json()

        # Verify filtered results
        assert data["totalResults"] == 1
        assert len(data["Resources"]) == 1
        assert data["Resources"][0]["id"] == test_user.id
        assert data["Resources"][0]["meta"]["resourceType"] == "User"

        # Filter groups by id
        response = client.get(f"/scim/v2/?filter=id eq {test_group.id}")
        assert response.status_code == 200
        data = response.json()

        # Verify filtered results
        assert data["totalResults"] == 1
        assert len(data["Resources"]) == 1
        assert data["Resources"][0]["id"] == test_group.id
        assert data["Resources"][0]["meta"]["resourceType"] == "Group"

    @pytest.mark.asyncio
    async def test_filter_by_id_url_encoded(
        self, client: TestClient, create_random_user: CreateUserFactory, create_random_group: CreateGroupFactory
    ) -> None:
        # First create a user and group
        test_user = await create_random_user()
        test_group = await create_random_group()

        # Filter users by id
        encoded_filter = urllib.parse.quote(f"externalId eq {test_user.external_id}")
        response = client.get(f"/scim/v2/?filter={encoded_filter}")
        assert response.status_code == 200
        data = response.json()

        # Verify filtered results
        assert data["totalResults"] == 1
        assert len(data["Resources"]) == 1
        assert data["Resources"][0]["id"] == test_user.id
        assert data["Resources"][0]["meta"]["resourceType"] == "User"

        # Filter groups by id
        encoded_filter = urllib.parse.quote(f"externalId eq {test_group.external_id}")
        response = client.get(f"/scim/v2/?filter={encoded_filter}")
        assert response.status_code == 200
        data = response.json()

        # Verify filtered results
        assert data["totalResults"] == 1
        assert len(data["Resources"]) == 1
        assert data["Resources"][0]["id"] == test_group.id
        assert data["Resources"][0]["meta"]["resourceType"] == "Group"
