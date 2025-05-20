# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import Singleton

from univention.scim.server.authn.authn import Authentication
from univention.scim.server.authn.oidc_configuration import OpenIDConnectConfiguration
from univention.scim.server.authz.authz import Authorization
from univention.scim.server.config import ApplicationSettings, application_settings, dependency_injection_settings
from univention.scim.server.domain.group_service import GroupService
from univention.scim.server.domain.repo.container import RepositoryContainer
from univention.scim.server.domain.user_service import UserService
from univention.scim.server.model_service.load_schemas import LoadSchemas


# Concrete implementations / adapters can be overwritten by setting them as env vars for DependencyInjectionSettings.
di = dependency_injection_settings()


class ApplicationContainer(DeclarativeContainer):
    settings: ApplicationSettings = Singleton(application_settings)

    # Initialize repository container for CRUD operations
    repo_config = settings().udm.model_dump()
    repo_config["base_url"] = f"{settings().host}{settings().api_prefix}"
    repo_config["url"] = repo_config["url"].rstrip("/") + "/"

    repositories: RepositoryContainer = Singleton(RepositoryContainer)
    repositories().config.from_dict(repo_config)

    # Use repositories from the repository container if specified in DI settings
    # Otherwise use the default implementations
    if di.di_user_repo == "univention.scim.server.domain.repo.container.RepositoryContainer.user_crud_manager":
        user_repo = repositories.provided.user_crud_manager()
    else:
        user_repo = Singleton(di.di_user_repo)

    user_service: UserService = Singleton(di.di_user_service, user_repository=user_repo)

    if di.di_group_repo == "univention.scim.server.domain.repo.container.RepositoryContainer.group_crud_manager":
        group_repo = repositories.provided.group_crud_manager()
    else:
        group_repo = Singleton(di.di_group_repo)

    group_service: GroupService = Singleton(di.di_group_service, group_repository=group_repo)
    schema_loader: LoadSchemas = Singleton(di.di_schema_loader)

    if settings().auth_enabled:
        oidc_configuration: OpenIDConnectConfiguration = Singleton(
            di.di_oidc_configuration, config=settings().authenticator
        )
        authenticator: Authentication = Singleton(
            di.di_authenticator, oidc_configuration=oidc_configuration, client_id=settings().authenticator.client_id
        )
        # TODO: Switch to using our own UserService if group mapping is implemented.
        # For now use the UDM REST API directly
        authorization: Authorization = Singleton(
            di.di_authorization, group_dn=settings().authenticator.allow_group_dn, udm_settings=settings().udm
        )
