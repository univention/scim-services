# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

from functools import lru_cache
from typing import Annotated

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
    api_prefix: Annotated[str, Field("/scim/v2", env="API_PREFIX")]

    # Logging
    log_level: Annotated[str, Field("INFO", env="LOG_LEVEL")]

    # Server
    host: Annotated[str, Field("0.0.0.0", env="HOST")]
    port: Annotated[int, Field(8000, env="PORT")]

    # CORS
    cors_origins: Annotated[list[str], Field(["*"], env="CORS_ORIGINS")]

    # Authentication and authorization
    auth_enabled: Annotated[bool, Field(True, env="AUTH_ENABLED")]
    authenticator: AuthenticatorConfig

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "case_sensitive": False}


class DependencyInjectionSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file="dependency-injection.env", env_file_encoding="utf-8")

    # TODO: change for real implementation, allow all just for dev now
    di_authenticator: str = "univention.scim.server.authn.authn_impl.AllowAllBearerAuthentication"


@lru_cache(maxsize=1)
def application_settings() -> ApplicationSettings:
    authenticator = AuthenticatorConfig()
    return ApplicationSettings(authenticator=authenticator)


@lru_cache(maxsize=1)
def dependency_injection_settings() -> DependencyInjectionSettings:
    return DependencyInjectionSettings()
