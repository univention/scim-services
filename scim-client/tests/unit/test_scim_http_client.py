# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2026 Univention GmbH

import unittest.mock as um
import uuid

import pytest
from pytest_httpserver import HTTPServer
from scim2_models import (
    Email,
    InvalidValueException,
    NotFoundException,
    Role,
    SCIMException,
    UnauthorizedException,
    UniquenessException,
    User,
)

import univention.scim.client.scim_client_settings as scs
import univention.scim.client.scim_http_client as shc


class TestMakeScimClient:
    @pytest.fixture
    def mocked_scim_client(self, monkeypatch):
        monkeypatch.setattr(shc, "ScimClient", um.Mock())
        return shc.ScimClient

    @pytest.fixture
    def mocked_wire_com_scim_client(self, monkeypatch):
        monkeypatch.setattr(shc, "WireComScimClient", um.Mock())
        return shc.WireComScimClient

    @pytest.mark.parametrize("scheme", ["http", "https"])
    @pytest.mark.parametrize("url_tail", ["some.host.org/and/a/path", "some.host.org", "1.2.3.4/and/a/path", "1.2.3.4"])
    def test_returns_basic_client(self, mocked_scim_client, scheme, url_tail):
        url = f"{scheme}://{url_tail}"
        settings = scs.ScimConsumerSettings(scim_server_base_url=url)  # pyright: ignore[reportCallIssue]
        client = shc.make_scim_client(None, settings)
        mocked_scim_client.assert_called_once_with(None, settings)
        assert client is mocked_scim_client.return_value

    @pytest.mark.parametrize("scheme", ["http", "https"])
    @pytest.mark.parametrize(
        "url_tail", ["wire.com/and/a/path", "wire.com", "some.subdomain.wire.com/and/a/path", "some.subdomain.wire.com"]
    )
    def test_returns_wire_com_client_for_wire_com_urls(self, mocked_wire_com_scim_client, scheme, url_tail):
        url = f"{scheme}://{url_tail}"
        settings = scs.ScimConsumerSettings(scim_server_base_url=url)  # pyright: ignore[reportCallIssue]
        client = shc.make_scim_client(None, settings)
        mocked_wire_com_scim_client.assert_called_once_with(None, settings)
        assert client is mocked_wire_com_scim_client.return_value


class TestWireComScimClient:
    """
    Tests for wire.com quirks.

    These tests mock some of the responses of the wire.com SCIM server that
    have been observed in the wild. We're testing mostly that the client
    doesn't fail in unexpected ways.

    This includes in particular that the client can deal with wire.com's
    incorrect responses in /ServiceProviderConfig and doesn't rely on
    automatic schema discovery.
    """

    @pytest.fixture
    def httpserver(self, httpserver: HTTPServer):
        yield httpserver
        httpserver.check()

    @pytest.fixture(autouse=True)
    def set_up_mock_server(self, httpserver: HTTPServer):
        service_provider_config = {
            "authenticationSchemes": [
                {
                    "description": "Authentication via the HTTP Basic standard",
                    "documentationUri": "https://en.wikipedia.org/wiki/Basic_access_authentication",
                    "name": "HTTP Basic",
                    "specUri": "https://tools.ietf.org/html/rfc7617",
                    "type": "httpbasic",
                }
            ],
            "bulk": {"maxOperations": 0, "maxPayloadSize": 0, "supported": False},
            "changePassword": {"supported": False},
            "etag": {"supported": False},
            "filter": {"maxResults": 0, "supported": False},
            "patch": {"supported": True},
            "schemas": [
                "urn:ietf:params:scim:schemas:core:2.0:User",
                "urn:ietf:params:scim:schemas:core:2.0:ServiceProviderConfig",
                "urn:ietf:params:scim:schemas:core:2.0:Group",
                "urn:ietf:params:scim:schemas:core:2.0:Schema",
                "urn:ietf:params:scim:schemas:core:2.0:ResourceType",
            ],
            "sort": {"supported": False},
        }
        httpserver.expect_request("/ServiceProviderConfig", method="GET").respond_with_json(
            service_provider_config, status=200, content_type="application/scim+json;charset=utf-8"
        )

    @pytest.fixture
    def client(self, httpserver):
        settings = scs.ScimConsumerSettings(
            scim_server_base_url=httpserver.url_for(""),
        )  # pyright: ignore[reportCallIssue]
        return shc.WireComScimClient(None, settings)

    @pytest.fixture
    def user(self):
        return User(
            user_name="username1",
            external_id=str(uuid.uuid4()),
            emails=[Email(value="a@b.net")],
            display_name="display_name1",
            roles=[Role(value="member")],
        )

    @pytest.fixture
    def user_response(self, user: User):
        wire_com_id = uuid.uuid4()
        assert isinstance(user.emails, list)
        return {
            "active": False,
            "displayName": user.display_name,
            "emails": [{"value": user.emails[0].value}],
            "externalId": user.external_id,
            "id": str(wire_com_id),
            "meta": {
                "created": "2026-11-04T07:40:00.331Z",
                "lastModified": "2026-11-04T07:40:00.331Z",
                "location": f"https://prod-nginz-https.wire.com/scim/v2/Users/{wire_com_id}",
                "resourceType": "User",
                "version": 'W/"3278227fa523d67bbe1b593ae60c35652ac82261e2144d2a0a23b20b6f4b594e"',
            },
            "preferredLanguage": "en",
            "roles": [{"value": "member"}],
            "schemas": [
                "urn:ietf:params:scim:schemas:core:2.0:User",
                "urn:wire:scim:schemas:profile:1.0",
                "urn:ietf:params:scim:schemas:extension:wire:1.0:User",
            ],
            "urn:ietf:params:scim:schemas:extension:wire:1.0:User": {},
            "urn:wire:scim:schemas:profile:1.0": {"richInfo": {"fields": [], "version": 0}},
            "userName": user.user_name,
        }

    def test_create_user(self, client: shc.WireComScimClient, httpserver: HTTPServer, user: User, user_response):
        httpserver.expect_request("/Users", method="POST").respond_with_json(
            user_response, status=201, content_type="application/scim+json;charset=utf-8"
        )

        client.create_resource(user)

    def test_create_user_auth_failed(self, client: shc.WireComScimClient, httpserver: HTTPServer, user: User):
        response = {
            "detail": "authorization failed: Invalid SCIM token",
            "schemas": ["urn:ietf:params:scim:api:messages:2.0:Error"],
            "status": "401",
        }
        httpserver.expect_request("/Users", method="POST").respond_with_json(
            response, status=401, content_type="application/scim+json;charset=utf-8"
        )

        with pytest.raises(UnauthorizedException):
            client.create_resource(user)

    def test_create_user_conflict(self, client: shc.WireComScimClient, httpserver: HTTPServer, user: User):
        response = {
            "detail": "userName is already taken",
            "schemas": ["urn:ietf:params:scim:api:messages:2.0:Error"],
            "scimType": "uniqueness",
            "status": "409",
        }
        httpserver.expect_request("/Users", method="POST").respond_with_json(
            response, status=409, content_type="application/scim+json;charset=utf-8"
        )

        with pytest.raises(UniquenessException):
            client.create_resource(user)

    def test_create_user_external_id_without_email(self, client: shc.WireComScimClient, httpserver: HTTPServer):
        response = {
            "detail": "Could not process externalId. Please check: (1) ... snip ...",
            "schemas": ["urn:ietf:params:scim:api:messages:2.0:Error"],
            "scimType": "invalidValue",
            "status": "400",
        }
        httpserver.expect_request("/Users", method="POST").respond_with_json(
            response, status=400, content_type="application/scim+json;charset=utf-8"
        )

        user = User(user_name="u1", external_id=str(uuid.uuid4()))
        with pytest.raises(InvalidValueException):
            client.create_resource(user)

    def test_update_user(self, client: shc.WireComScimClient, httpserver: HTTPServer, user: User, user_response):
        httpserver.expect_request(f"/Users/{user_response['id']}", method="PUT").respond_with_json(
            user_response, status=200, content_type="application/scim+json;charset=utf-8"
        )

        user.id = user_response["id"]
        client.update_resource(user)

    def test_update_user_not_found(self, client: shc.WireComScimClient, httpserver: HTTPServer, user: User):
        nonexistent_id = str(uuid.uuid4())
        response = {
            "detail": "User ae350551-064f-49bc-8319-5104fb0534b1 not found",
            "schemas": ["urn:ietf:params:scim:api:messages:2.0:Error"],
            "status": "404",
        }
        httpserver.expect_request(f"/Users/{nonexistent_id}", method="PUT").respond_with_json(
            response, status=404, content_type="application/scim+json;charset=utf-8"
        )

        user.id = nonexistent_id
        with pytest.raises(NotFoundException):
            client.update_resource(user)

    def test_delete_user(self, client: shc.WireComScimClient, httpserver: HTTPServer):
        """
        For deletions, the server always returns an empty 204, no matter if
        the user existed or not.
        """
        user_id = str(uuid.uuid4())
        httpserver.expect_request(f"/Users/{user_id}", method="DELETE").respond_with_data(b"", status=204)

        client.delete_resource(user_id, User)

    def test_get_resource(self, client: shc.WireComScimClient, httpserver: HTTPServer, user: User, user_response):
        response = {
            "Resources": [user_response],
            "itemsPerPage": 1,
            "schemas": ["urn:ietf:params:scim:api:messages:2.0:ListResponse"],
            "startIndex": 1,
            "totalResults": 1,
        }
        query = {"filter": f'externalId eq "{user.external_id}"'}
        httpserver.expect_request("/Users", query_string=query, method="GET").respond_with_json(response, status=200)

        queried_user = client.get_resource(str(user.external_id), User)
        assert queried_user == user_response

    def test_get_resource_with_no_results(self, client: shc.WireComScimClient, httpserver: HTTPServer):
        external_id = uuid.uuid4()
        response = {
            "Resources": [],
            "itemsPerPage": 0,
            "schemas": ["urn:ietf:params:scim:api:messages:2.0:ListResponse"],
            "startIndex": 1,
            "totalResults": 0,
        }
        query = {"filter": f'externalId eq "{external_id}"'}
        httpserver.expect_request("/Users", query_string=query, method="GET").respond_with_json(response, status=200)

        with pytest.raises(shc.ScimClientNoDataFoundException):
            client.get_resource(str(external_id), User)

    def test_get_resource_with_multiple_results(
        self, client: shc.WireComScimClient, httpserver: HTTPServer, user: User, user_response
    ):
        # This doesn't actually happen in reality with the same user being returned twice, but let's test the
        # too-many-results path anyway.
        user_response2 = user_response.copy()
        response = {
            "Resources": [user_response, user_response2],
            "itemsPerPage": 2,
            "schemas": ["urn:ietf:params:scim:api:messages:2.0:ListResponse"],
            "startIndex": 1,
            "totalResults": 2,
        }
        query = {"filter": f'externalId eq "{user.external_id}"'}
        httpserver.expect_request("/Users", query_string=query, method="GET").respond_with_json(response, status=200)

        with pytest.raises(shc.ScimClientTooManyResultsException):
            client.get_resource(str(user.external_id), User)

    def test_get_resource_with_bugged_filter(self, client: shc.WireComScimClient, httpserver: HTTPServer):
        """
        This particular test checks for error responses that don't return a
        JSON. This has not been observed with the filter tested here (eq), but
        with the simpler pr filter.
        """
        external_id = uuid.uuid4()
        query = {"filter": f'externalId eq "{external_id}"'}
        response = "Error parsing query parameter filter failed: Failed reading: empty"
        httpserver.expect_request("/Users", query_string=query, method="GET").respond_with_data(response, status=400)

        with pytest.raises(SCIMException) as excinfo:
            client.get_resource(str(external_id), User)
        assert excinfo.value.detail == response
