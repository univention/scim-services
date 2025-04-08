# scim-server/src/univention/scim/server/domain/repo/container.py
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
    scim2udm_mapper = providers.Singleton(ScimToUdmMapper)

    udm2scim_mapper = providers.Singleton(UdmToScimMapper)

    # Repository factories
    user_repository = providers.Factory(
        CrudUdm[User],
        resource_type="User",
        scim2udm_mapper=scim2udm_mapper,
        udm2scim_mapper=udm2scim_mapper,
        resource_class=User,
    )

    group_repository = providers.Factory(
        CrudUdm[Group],
        resource_type="Group",
        scim2udm_mapper=scim2udm_mapper,
        udm2scim_mapper=udm2scim_mapper,
        resource_class=Group,
    )

    # CRUD Manager factories
    user_crud_manager = providers.Factory(CrudManager[User], primary_repository=user_repository, resource_type="User")

    group_crud_manager = providers.Factory(
        CrudManager[Group], primary_repository=group_repository, resource_type="Group"
    )

    # Generic factory method for creating crud managers for any resource type
    # This is provided for backward compatibility and explicit creation
    @staticmethod
    def create_for_udm(resource_type: str, resource_class: type[T]) -> CrudManager[T]:
        """
        Create a CrudManager that uses UDM as the primary repository.
        This is a static helper method that doesn't use the container providers,
        intended for situations where direct instantiation is needed.

        Args:
            resource_type: The type of resource to manage ('User' or 'Group')
            resource_class: The class of resource being managed (e.g., User, Group)
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
        )

        return CrudManager(primary_repo, resource_type)
