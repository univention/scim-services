# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

from typing import TypeVar

from dependency_injector import containers, providers
from scim2_models import Group, Resource, User

from univention.scim.server.domain.repo.crud_manager import CrudManager
from univention.scim.server.domain.repo.udm.crud_udm import CrudUdm
from univention.scim.server.model_service.scim2udm import ScimToUdmMapper
from univention.scim.server.model_service.udm2scim import UdmToScimMapper


T = TypeVar("T", bound=Resource)


class RepositoryContainer(containers.DeclarativeContainer):
    """Container for repository-related dependencies."""

    config = providers.Configuration()

    # Mappers
    scim2udm_mapper: ScimToUdmMapper = providers.Singleton(ScimToUdmMapper)

    udm2scim_mapper: UdmToScimMapper = providers.Singleton(UdmToScimMapper)

    # Repository factories
    user_repository: CrudUdm[User] = providers.Factory(
        CrudUdm[User],
        resource_type="User",
        scim2udm_mapper=scim2udm_mapper,
        udm2scim_mapper=udm2scim_mapper,
        resource_class=User,
        udm_url=config.settings.udm.udm_url,
        udm_username=config.settings.udm.udm_username,
        udm_password=config.settings.udm.udm_password,
    )

    group_repository: CrudUdm[Group] = providers.Factory(
        CrudUdm[Group],
        resource_type="Group",
        scim2udm_mapper=scim2udm_mapper,
        udm2scim_mapper=udm2scim_mapper,
        resource_class=Group,
        udm_url=config.settings.udm.udm_url,
        udm_username=config.settings.udm.udm_username,
        udm_password=config.settings.udm.udm_password,
    )

    # CRUD Manager factories
    user_crud_manager: CrudManager[User] = providers.Factory(
        CrudManager[User], primary_repository=user_repository, resource_type="User"
    )

    group_crud_manager: CrudManager[Group] = providers.Factory(
        CrudManager[Group], primary_repository=group_repository, resource_type="Group"
    )

    # Generic factory method for creating crud managers for any resource type
    # This is provided for backward compatibility and explicit creation
    @staticmethod
    def create_for_udm(
        resource_type: str, resource_class: type[T], udm_url: str, udm_username: str, udm_password: str
    ) -> CrudManager[T]:
        """
        Create a CrudManager that uses UDM as the primary repository.
        This is a static helper method that doesn't use the container providers,
        intended for situations where direct instantiation is needed.

        Args:
            resource_type: The type of resource to manage ('User' or 'Group')
            resource_class: The class of resource being managed (e.g., User, Group)
            udm_url: URL of the UDM REST API
            udm_username: Username for UDM authentication
            udm_password: Password for UDM authentication
        Returns:
            A CrudManager instance configured for UDM
        """
        scim2udm_mapper = ScimToUdmMapper()
        udm2scim_mapper = UdmToScimMapper()

        primary_repo = CrudUdm(
            resource_type=resource_type,
            scim2udm_mapper=scim2udm_mapper,
            udm2scim_mapper=udm2scim_mapper,
            resource_class=resource_class,
            udm_url=udm_url,
            udm_username=udm_username,
            udm_password=udm_password,
        )

        return CrudManager(primary_repo, resource_type)
