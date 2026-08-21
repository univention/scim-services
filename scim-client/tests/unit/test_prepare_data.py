# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

from unittest.mock import MagicMock

import pytest
from scim2_models import EnterpriseUser, Group, Resource

from univention.scim.client.scim_client import ScimConsumer
from univention.scim.client.scim_client_settings import ScimConsumerSettings
from univention.scim.server.models.extensions.customer1_user import Customer1User
from univention.scim.server.models.extensions.univention_user import UniventionUser
from univention.scim.server.models.user import User

from ..data.provisioning_message_factory import get_provisioning_message_data


class _MinimalDiscoveredUser(Resource):
    """A discovered User model exposing only the base Resource fields (id/externalId/meta/
    schemas)"""


class _MinimalDiscoveredGroup(Resource):
    """A discovered server group model whose /Schemas response for core Group declares
    only the base Resource fields."""


@pytest.fixture
def settings() -> ScimConsumerSettings:
    return ScimConsumerSettings(
        scim_server_base_url="https://example.com/scim/v2",
        scim_auth_method="none",
        health_check_enabled=False,
        external_id_user_mapping="univentionObjectIdentifier",
        external_id_group_mapping="univentionObjectIdentifier",
    )


def _build_udm_object(data_type: str) -> object:
    data = get_provisioning_message_data(data_type)
    assert data is not None
    return type("Obj", (object,), data["body"]["new"])()


@pytest.mark.parametrize("server_supports_enterprise", [True, False])
def test_prepare_data_gates_enterprise_extension_by_discovery(
    settings: ScimConsumerSettings, server_supports_enterprise: bool
) -> None:
    scim_http_client = MagicMock()
    discovered_model = User[EnterpriseUser] if server_supports_enterprise else User
    scim_http_client.get_client.return_value.get_resource_model.return_value = discovered_model

    consumer = ScimConsumer(scim_http_client, MagicMock(), settings)
    udm_object = _build_udm_object("user_create")

    scim_resource = consumer.prepare_data(udm_object, "users/user")

    assert (EnterpriseUser.to_schema().id in scim_resource.schemas) is server_supports_enterprise


@pytest.mark.parametrize("server_supports_univention", [True, False])
def test_prepare_data_gates_univention_extension_by_discovery(
    settings: ScimConsumerSettings, server_supports_univention: bool
) -> None:
    scim_http_client = MagicMock()
    discovered_model = User[UniventionUser] if server_supports_univention else User
    scim_http_client.get_client.return_value.get_resource_model.return_value = discovered_model

    consumer = ScimConsumer(scim_http_client, MagicMock(), settings)
    udm_object = _build_udm_object("user_create")
    udm_object.properties["description"] = "Some description"

    scim_resource = consumer.prepare_data(udm_object, "users/user")

    assert (UniventionUser.to_schema().id in scim_resource.schemas) is server_supports_univention
    if server_supports_univention:
        assert scim_resource.UniventionUser.description == "Some description"


@pytest.mark.parametrize("server_supports_customer1", [True, False])
def test_prepare_data_gates_customer1_extension_by_discovery(
    settings: ScimConsumerSettings, server_supports_customer1: bool
) -> None:
    scim_http_client = MagicMock()
    discovered_model = User[Customer1User] if server_supports_customer1 else User
    scim_http_client.get_client.return_value.get_resource_model.return_value = discovered_model

    consumer = ScimConsumer(scim_http_client, MagicMock(), settings)
    udm_object = _build_udm_object("user_create")
    udm_object.properties["primaryOrgUnit"] = "Sales"

    scim_resource = consumer.prepare_data(udm_object, "users/user")

    assert (Customer1User.to_schema().id in scim_resource.schemas) is server_supports_customer1
    if server_supports_customer1:
        assert scim_resource.Customer1User.primary_org_unit == "Sales"


def test_prepare_data_includes_multiple_advertised_extensions_together(
    settings: ScimConsumerSettings,
) -> None:
    scim_http_client = MagicMock()
    scim_http_client.get_client.return_value.get_resource_model.return_value = User[
        EnterpriseUser | UniventionUser | Customer1User
    ]

    consumer = ScimConsumer(scim_http_client, MagicMock(), settings)
    udm_object = _build_udm_object("user_create")

    scim_resource = consumer.prepare_data(udm_object, "users/user")

    assert EnterpriseUser.to_schema().id in scim_resource.schemas
    assert UniventionUser.to_schema().id in scim_resource.schemas
    assert Customer1User.to_schema().id in scim_resource.schemas


def test_prepare_data_drops_any_attribute_not_advertised_by_server(
    settings: ScimConsumerSettings,
) -> None:
    # A server whose discovered core User schema declares nothing beyond the base Resource
    # fields (e.g. a reduced schema built via Resource.from_schema from its own /Schemas
    # response) -- every other attribute should be dropped, not just a hardcoded subset,
    # while id/externalId/meta/schemas are always kept.
    scim_http_client = MagicMock()
    scim_http_client.get_client.return_value.get_resource_model.return_value = _MinimalDiscoveredUser

    consumer = ScimConsumer(scim_http_client, MagicMock(), settings)
    udm_object = _build_udm_object("user_create")
    udm_object.properties["phone"] = ["12345"]
    udm_object.properties["street"] = "Test Street"
    udm_object.properties["guardianRoles"] = ["Role1"]
    udm_object.properties["jpegPhoto"] = "base64encodedimagedata"

    scim_resource = consumer.prepare_data(udm_object, "users/user")

    assert scim_resource.phone_numbers is None
    assert scim_resource.addresses is None
    assert scim_resource.roles is None
    assert scim_resource.photos is None
    # not one of the originally hardcoded attributes
    assert scim_resource.display_name is None
    # base Resource fields are always present on the discovered model too, so never dropped
    assert scim_resource.external_id is not None


def test_prepare_data_keeps_optional_core_attributes_when_advertised_by_server(
    settings: ScimConsumerSettings,
) -> None:
    scim_http_client = MagicMock()
    scim_http_client.get_client.return_value.get_resource_model.return_value = User

    consumer = ScimConsumer(scim_http_client, MagicMock(), settings)
    udm_object = _build_udm_object("user_create")
    udm_object.properties["phone"] = ["12345"]
    udm_object.properties["street"] = "Test Street"
    udm_object.properties["guardianRoles"] = ["Role1"]

    scim_resource = consumer.prepare_data(udm_object, "users/user")

    assert scim_resource.phone_numbers is not None
    assert scim_resource.addresses is not None
    assert scim_resource.roles is not None


def test_prepare_data_drops_any_group_attribute_not_advertised_by_server(
    settings: ScimConsumerSettings,
) -> None:
    scim_http_client = MagicMock()
    scim_http_client.get_client.return_value.get_resource_model.return_value = _MinimalDiscoveredGroup

    consumer = ScimConsumer(scim_http_client, MagicMock(), settings)
    udm_object = _build_udm_object("group_create")

    scim_resource = consumer.prepare_data(udm_object, "groups/group")

    assert scim_resource.display_name is None
    assert scim_resource.external_id is not None


def test_prepare_data_keeps_group_attributes_when_advertised_by_server(
    settings: ScimConsumerSettings,
) -> None:
    scim_http_client = MagicMock()
    scim_http_client.get_client.return_value.get_resource_model.return_value = Group

    consumer = ScimConsumer(scim_http_client, MagicMock(), settings)
    udm_object = _build_udm_object("group_create")

    scim_resource = consumer.prepare_data(udm_object, "groups/group")

    assert scim_resource.display_name is not None
