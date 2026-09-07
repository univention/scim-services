# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

from collections.abc import Iterator
from contextlib import contextmanager
from unittest.mock import MagicMock, patch

import pytest
from scim2_client import SCIMResponseError
from scim2_models import AuthenticationScheme, Filter, ResourceType, ServiceProviderConfig

from univention.scim.client.scim_client_settings import ScimConsumerSettings
from univention.scim.client.scim_http_client import ScimClient


def _settings(**overrides: object) -> ScimConsumerSettings:
    defaults: dict[str, object] = {
        "scim_server_base_url": "https://example.com/scim/v2",
        "scim_auth_method": "none",
        "health_check_enabled": False,
        "group_sync_enabled": False,
    }
    defaults.update(overrides)
    return ScimConsumerSettings(**defaults)  # type: ignore[arg-type]


def _service_provider_config(
    *, filter_supported: bool = True, scheme_types: list[AuthenticationScheme.Type] | None = None
) -> ServiceProviderConfig:
    scheme_types = scheme_types if scheme_types is not None else [AuthenticationScheme.Type.oauthbearertoken]
    return ServiceProviderConfig(
        filter=Filter(supported=filter_supported),
        authentication_schemes=[
            AuthenticationScheme(type=scheme_type, name=scheme_type.value, description=scheme_type.value)
            for scheme_type in scheme_types
        ],
    )


_MISSING = object()


@contextmanager
def _scim_client(
    settings: ScimConsumerSettings,
    *,
    resource_type_discovery_fails: bool = False,
    service_provider_config_discovery_fails: bool = False,
    service_provider_config: ServiceProviderConfig | None = _MISSING,  # type: ignore[assignment]
    user_resource_type: bool = True,
    group_resource_type: bool = True,
) -> Iterator[ScimClient]:
    """Patches SyncSCIMClient/Client and yields a ScimClient ready for _create_client()."""
    if service_provider_config is _MISSING:
        service_provider_config = _service_provider_config()

    def get_resource_model(name: str) -> MagicMock | None:
        if resource_type_discovery_fails:
            return None
        if name == "User":
            return MagicMock() if user_resource_type else None
        if name == "Group":
            return MagicMock() if group_resource_type else None
        return MagicMock()

    def discover(*, schemas: bool = True, resource_types: bool = True, service_provider_config: bool = True) -> None:
        if (schemas or resource_types) and resource_type_discovery_fails:
            raise SCIMResponseError("simulated: server does not implement /ResourceTypes or /Schemas")
        if service_provider_config and service_provider_config_discovery_fails:
            raise SCIMResponseError("simulated: server does not implement /ServiceProviderConfig")

    mock_instance = MagicMock()
    mock_instance.get_resource_model.side_effect = get_resource_model
    mock_instance.discover.side_effect = discover
    mock_instance.service_provider_config = None if service_provider_config_discovery_fails else service_provider_config

    with (
        patch("univention.scim.client.scim_http_client.SyncSCIMClient", return_value=mock_instance),
        patch("univention.scim.client.scim_http_client.Client"),
    ):
        yield ScimClient(auth=None, settings=settings)


@pytest.mark.parametrize(
    "auth_method,required_scheme_type",
    [
        ("oidc", AuthenticationScheme.Type.oauthbearertoken),
        ("bearer", AuthenticationScheme.Type.oauthbearertoken),
        ("basic", AuthenticationScheme.Type.httpbasic),
    ],
)
def test_auth_scheme_present_succeeds(auth_method: str, required_scheme_type: AuthenticationScheme.Type) -> None:
    spc = _service_provider_config(scheme_types=[required_scheme_type])
    with _scim_client(_settings(scim_auth_method=auth_method), service_provider_config=spc) as scim_client:
        scim_client._create_client()


def test_auth_method_none_skips_scheme_check() -> None:
    spc = _service_provider_config(scheme_types=[])
    with _scim_client(_settings(scim_auth_method="none"), service_provider_config=spc) as scim_client:
        scim_client._create_client()


def test_missing_group_resource_type_with_group_sync_disabled_succeeds() -> None:
    with _scim_client(_settings(group_sync_enabled=False), group_resource_type=False) as scim_client:
        scim_client._create_client()


def test_health_check_queries_resource_type_not_service_provider_config() -> None:
    with _scim_client(_settings()) as scim_client:
        scim_client._scim_client = scim_client._create_client()
        scim_client._scim_client.query.reset_mock()

        assert scim_client.health_check() is True

        scim_client._scim_client.query.assert_called_once_with(ResourceType)


def test_get_client_does_not_rediscover_when_healthy() -> None:
    with _scim_client(_settings(health_check_enabled=True)) as scim_client:
        scim_client.get_client()
        scim_client.get_client()
        scim_client.get_client()

        # discover() is called twice per _create_client(): once for resource types
        # and once for ServiceProviderConfig -- it must not run again on later
        # get_client() calls as long as the health check keeps passing.
        assert scim_client._scim_client.discover.call_count == 2
