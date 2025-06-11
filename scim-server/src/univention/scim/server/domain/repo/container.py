# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

from typing import TypeVar

from asgi_correlation_id import correlation_id as asgi_correlation_id
from dependency_injector import containers, providers
from loguru import logger
from scim2_models import Group, Resource, User
from univention.admin.rest.client import UDM

from univention.scim.server.config import ApplicationSettings
from univention.scim.server.domain.crud_scim import CrudScim
from univention.scim.server.domain.repo.crud_manager import CrudManager
from univention.scim.server.domain.repo.udm.crud_udm import CrudUdm
from univention.scim.server.domain.repo.udm.udm_id_cache import UdmIdCache
from univention.scim.server.models.types import GroupWithExtensions, UserWithExtensions
from univention.scim.transformation import ScimToUdmMapper, UdmToScimMapper


T = TypeVar("T", bound=Resource)


def _generate_udm_request_id() -> str:
    """
    Returns the upstream correlation ID for UDM requests to maintain
    the same correlation ID throughout the request chain.
    """
    upstream_correlation_id: str = str(asgi_correlation_id.get())
    logger.bind(
        correlation_id=upstream_correlation_id,
    ).debug("Using upstream correlation ID for UDM request in repository container.")
    return upstream_correlation_id


def _get_base_url(host: str, api_prefix: str) -> str:
    return f"{host}{api_prefix}"


class RepositoryContainer(containers.DeclarativeContainer):
    """Container for repository-related dependencies."""

    settings = providers.Dependency(instance_of=ApplicationSettings)

    udm_client: UDM = providers.Singleton(
        UDM.http,
        settings.provided.udm.url,
        settings.provided.udm.username,
        settings.provided.udm.password,
        request_id_generator=_generate_udm_request_id,
    )
    cache: UdmIdCache = providers.Singleton(UdmIdCache, udm_client, 120)

    # Mappers
    scim2udm_mapper: ScimToUdmMapper = providers.Singleton(ScimToUdmMapper, cache=cache)

    udm2scim_mapper: UdmToScimMapper = providers.Singleton(
        UdmToScimMapper[UserWithExtensions, GroupWithExtensions],
        cache=cache,
        user_type=UserWithExtensions,
        group_type=GroupWithExtensions,
    )

    # Repository factories
    user_repository: CrudScim[UserWithExtensions] = providers.Factory(
        CrudUdm[UserWithExtensions],
        resource_type="User",
        scim2udm_mapper=scim2udm_mapper,
        udm2scim_mapper=udm2scim_mapper,
        resource_class=User,
        udm_client=udm_client,
        base_url=providers.Callable(
            _get_base_url, host=settings.provided.host, api_prefix=settings.provided.api_prefix
        ),
    )

    group_repository: CrudScim[GroupWithExtensions] = providers.Factory(
        CrudUdm[GroupWithExtensions],
        resource_type="Group",
        scim2udm_mapper=scim2udm_mapper,
        udm2scim_mapper=udm2scim_mapper,
        resource_class=Group,
        udm_client=udm_client,
        base_url=providers.Callable(
            _get_base_url, host=settings.provided.host, api_prefix=settings.provided.api_prefix
        ),
    )

    # CRUD Manager factories
    user_crud_manager: CrudManager[UserWithExtensions] = providers.Factory(
        CrudManager[UserWithExtensions], primary_repository=user_repository, resource_type="User"
    )

    group_crud_manager: CrudManager[GroupWithExtensions] = providers.Factory(
        CrudManager[GroupWithExtensions], primary_repository=group_repository, resource_type="Group"
    )
