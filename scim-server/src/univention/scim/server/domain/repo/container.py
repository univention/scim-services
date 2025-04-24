# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

from typing import TypeVar

from dependency_injector import containers, providers
from scim2_models import Group, Resource, User

from univention.scim.server.domain.crud_scim import CrudScim
from univention.scim.server.domain.repo.crud_manager import CrudManager
from univention.scim.server.domain.repo.udm.crud_udm import CrudUdm
from univention.scim.transformation import ScimToUdmMapper, UdmToScimMapper


T = TypeVar("T", bound=Resource)


class RepositoryContainer(containers.DeclarativeContainer):
    """Container for repository-related dependencies."""

    config = providers.Configuration()

    # Mappers
    scim2udm_mapper: ScimToUdmMapper = providers.Singleton(ScimToUdmMapper)

    udm2scim_mapper: UdmToScimMapper = providers.Singleton(UdmToScimMapper)

    # Repository factories
    user_repository: CrudScim[User] = providers.Factory(
        CrudUdm[User],
        resource_type="User",
        scim2udm_mapper=scim2udm_mapper,
        udm2scim_mapper=udm2scim_mapper,
        resource_class=User,
        udm_url=config.url,
        udm_username=config.username,
        udm_password=config.password,
    )

    group_repository: CrudScim[Group] = providers.Factory(
        CrudUdm[Group],
        resource_type="Group",
        scim2udm_mapper=scim2udm_mapper,
        udm2scim_mapper=udm2scim_mapper,
        resource_class=Group,
        udm_url=config.url,
        udm_username=config.username,
        udm_password=config.password,
    )

    # CRUD Manager factories
    user_crud_manager: CrudManager[User] = providers.Factory(
        CrudManager[User], primary_repository=user_repository, resource_type="User"
    )

    group_crud_manager: CrudManager[Group] = providers.Factory(
        CrudManager[Group], primary_repository=group_repository, resource_type="Group"
    )
