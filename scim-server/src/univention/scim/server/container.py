# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import Singleton

# Internal imports
from univention.scim.server.config import application_settings, dependency_injection_settings


# Concrete implementations / adapters can be overwritten by setting them as env vars for DependencyInjectionSettings.
di = dependency_injection_settings()


# TODO: Not sure why but mypy complains about type of DeclarativeContainer -> ignore error for now
# subclass "DeclarativeContainer" (has type "Any")  [misc]
#     class ApplicationContainer(DeclarativeContainer):
class ApplicationContainer(DeclarativeContainer):  # type: ignore
    settings = Singleton(application_settings)

    authenticator = Singleton(di.di_authenticator, config=settings().authenticator)
