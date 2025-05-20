# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

from typing import TypeVar

from dependency_injector import containers, providers
from scim2_models import Group, Resource, User
from univention.admin.rest.client import UDM

from univention.scim.server.domain.crud_scim import CrudScim
from univention.scim.server.domain.repo.crud_manager import CrudManager
from univention.scim.server.domain.repo.udm.crud_udm import CrudUdm
from univention.scim.server.domain.repo.udm.udm_id_cache import UdmIdCache
from univention.scim.transformation import ScimToUdmMapper, UdmToScimMapper


T = TypeVar("T", bound=Resource)


class RepositoryContainer(containers.DeclarativeContainer):
    """Container for repository-related dependencies."""

    config = providers.Configuration()

    udm_client: UDM = providers.Singleton(UDM.http, config.url, config.username, config.password)
    cache: UdmIdCache = providers.Singleton(UdmIdCache, udm_client, 120)

    # Mappers
    scim2udm_mapper: ScimToUdmMapper = providers.Singleton(ScimToUdmMapper, cache=cache)

    udm2scim_mapper: UdmToScimMapper = providers.Singleton(UdmToScimMapper, cache=cache)

    # Repository factories
    user_repository: CrudScim[User] = providers.Factory(
        CrudUdm[User],
        resource_type="User",
        scim2udm_mapper=scim2udm_mapper,
        udm2scim_mapper=udm2scim_mapper,
        resource_class=User,
        udm_client=udm_client,
        base_url=config.base_url,
    )

    group_repository: CrudScim[Group] = providers.Factory(
        CrudUdm[Group],
        resource_type="Group",
        scim2udm_mapper=scim2udm_mapper,
        udm2scim_mapper=udm2scim_mapper,
        resource_class=Group,
        udm_client=udm_client,
        base_url=config.base_url,
    )

    # CRUD Manager factories
    user_crud_manager: CrudManager[User] = providers.Factory(
        CrudManager[User], primary_repository=user_repository, resource_type="User"
    )

    group_crud_manager: CrudManager[Group] = providers.Factory(
        CrudManager[Group], primary_repository=group_repository, resource_type="Group"
    )
