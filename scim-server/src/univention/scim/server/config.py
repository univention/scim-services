# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application settings with support for environment variables and .env files.

    All settings can be overridden using environment variables.
    """

    # API settings
    api_prefix: str = Field("/scim/v2", env="API_PREFIX")

    # Logging
    log_level: str = Field("INFO", env="LOG_LEVEL")

    # Server
    host: str = Field("0.0.0.0", env="HOST")
    port: int = Field(8000, env="PORT")

    # CORS
    cors_origins: list[str] = Field(["*"], env="CORS_ORIGINS")

    # Authentication and authorization
    auth_enabled: bool = Field(False, env="AUTH_ENABLED")

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "case_sensitive": False}


# Create global settings instance
settings = Settings()
