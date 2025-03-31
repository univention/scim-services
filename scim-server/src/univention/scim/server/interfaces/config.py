# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

from pydantic_settings import BaseSettings


class AuthenticatorConfig(BaseSettings):
    token_validation_endpoint: str
