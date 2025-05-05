# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

from functools import lru_cache

from lancelog import LogLevel
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AuthenticatorConfig(BaseSettings):
    model_config = SettingsConfigDict()
    idp_openid_configuration_url: str = ""


class UdmConfig(BaseSettings):
    """
    UDM REST API configuration settings.
    """

    model_config = SettingsConfigDict()

    url: str = Field(default="http://localhost:9979/univention/udm/")
    username: str = Field(default="admin")
    password: str = Field(default="univention")


class ApplicationSettings(BaseSettings):
    """
    Application settings with support for environment variables and .env files.
    All settings can be overridden using environment variables.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        env_nested_delimiter="_",
        env_nested_max_split=1,
        extra="allow",
    )

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
    authenticator: AuthenticatorConfig = AuthenticatorConfig()
    # UDM configuration
    udm: UdmConfig = UdmConfig()


class DependencyInjectionSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file="dependency-injection.env", env_file_encoding="utf-8", case_sensitive=False
    )

    di_oidc_configuration: str = "univention.scim.server.authn.oidc_configuration_impl.OpenIDConnectConfigurationImpl"
    di_authenticator: str = "univention.scim.server.authn.authn_impl.OpenIDConnectAuthentication"

    # Use UDM-backed repositories for users
    di_user_repo: str = "univention.scim.server.domain.repo.container.RepositoryContainer.user_crud_manager"
    di_group_repo: str = "univention.scim.server.domain.repo.container.RepositoryContainer.group_crud_manager"

    di_user_service: str = "univention.scim.server.domain.user_service_impl.UserServiceImpl"
    di_group_service: str = "univention.scim.server.domain.group_service_impl.GroupServiceImpl"
    di_schema_loader: str = "univention.scim.server.model_service.load_schemas_impl.LoadSchemasImpl"


@lru_cache(maxsize=1)
def application_settings() -> ApplicationSettings:
    return ApplicationSettings()


@lru_cache(maxsize=1)
def dependency_injection_settings() -> DependencyInjectionSettings:
    return DependencyInjectionSettings()
