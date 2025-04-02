# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import Singleton

# Internal imports
from univention.scim.server.config import application_settings, dependency_injection_settings


# Concrete implementations / adapters can be overwritten by setting them as env vars for DependencyInjectionSettings.
di = dependency_injection_settings()


class ApplicationContainer(DeclarativeContainer):
    settings = Singleton(application_settings)

    if settings().auth_enabled:
        authenticator = Singleton(di.di_authenticator, config=settings().authenticator)

    user_repo = Singleton(di.di_user_repo)
    user_service = Singleton(di.di_user_service, user_repository=user_repo)

    group_repo = Singleton(di.di_group_repo)
    group_service = Singleton(di.di_group_service, group_repository=group_repo)

    schema_loader = Singleton(di.di_schema_loader)
