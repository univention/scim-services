# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

import abc

from .config import AuthenticatorConfig


class Authenticator(abc.ABC):
    def __init__(self, config: AuthenticatorConfig):
        self.config = config

    @abc.abstractmethod
    def validate(self, token: str) -> bool: ...
