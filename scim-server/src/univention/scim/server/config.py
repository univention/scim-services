# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH
from functools import lru_cache
from typing import Annotated

from lancelog import LogLevel
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AuthenticatorConfig(BaseSettings):
    token_validation_endpoint: Annotated[str, Field("", env="TOKEN_VALIDATION_ENDPOINT")]


class ApplicationSettings(BaseSettings):
    """
    Application settings with support for environment variables and .env files.
    All settings can be overridden using environment variables.
    """

    # API settings
    api_prefix: str = "/scim/v2"
    # Logging
    log_level: LogLevel = LogLevel.INFO
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    # CORS
    cors_origins: list[str] = ["*"]
    # Authentication and authorization
    auth_enabled: bool = True
    authenticator: AuthenticatorConfig
    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "case_sensitive": False}


class DependencyInjectionSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file="dependency-injection.env", env_file_encoding="utf-8")
    # TODO: change for real implementation, allow all just for dev now
    di_authenticator: str = "univention.scim.server.authn.authn_impl.AllowAllBearerAuthentication"

    # Use in-memory implementation by default, but can be overridden to use UDM repositories
    # Set these to "univention.scim.server.domain.repo.container.RepositoryContainer.user_crud_manager"
    # to use the UDM-backed repositories
    di_user_repo: str = "univention.scim.server.domain.repo.crud_scim_impl.CrudScimImpl"
    di_group_repo: str = "univention.scim.server.domain.repo.crud_scim_impl.CrudScimImpl"

    di_user_service: str = "univention.scim.server.domain.user_service_impl.UserServiceImpl"
    di_group_service: str = "univention.scim.server.domain.group_service_impl.GroupServiceImpl"
    di_schema_loader: str = "univention.scim.server.model_service.load_schemas_impl.LoadSchemasImpl"


@lru_cache(maxsize=1)
def application_settings() -> ApplicationSettings:
    authenticator = AuthenticatorConfig()
    return ApplicationSettings(authenticator=authenticator)


@lru_cache(maxsize=1)
def dependency_injection_settings() -> DependencyInjectionSettings:
    return DependencyInjectionSettings()
