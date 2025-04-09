# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH
from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import Singleton

# Internal imports
from univention.scim.server.config import application_settings, dependency_injection_settings
from univention.scim.server.domain.repo.container import RepositoryContainer


# Concrete implementations / adapters can be overwritten by setting them as env vars for DependencyInjectionSettings.
di = dependency_injection_settings()


class ApplicationContainer(DeclarativeContainer):
    settings = Singleton(application_settings)

    # Initialize repository container for CRUD operations
    repositories = Singleton(RepositoryContainer)

    if settings().auth_enabled:
        oidc_configuration = Singleton(di.di_oidc_configuration, config=settings().authenticator)
        authenticator = Singleton(di.di_authenticator, oidc_configuration=oidc_configuration)

    # Use repositories from the repository container if specified in DI settings
    # Otherwise use the default implementations
    if di.di_user_repo == "univention.scim.server.domain.repo.container.RepositoryContainer.user_crud_manager":
        user_repo = repositories.user_crud_manager
    else:
        user_repo = Singleton(di.di_user_repo)

    user_service = Singleton(di.di_user_service, user_repository=user_repo)

    if di.di_group_repo == "univention.scim.server.domain.repo.container.RepositoryContainer.group_crud_manager":
        group_repo = repositories.group_crud_manager
    else:
        group_repo = Singleton(di.di_group_repo)

    group_service = Singleton(di.di_group_service, group_repository=group_repo)
    schema_loader = Singleton(di.di_schema_loader)
