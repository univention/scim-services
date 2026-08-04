# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

import httpx
from pydantic import PrivateAttr
from pydantic_settings import BaseSettings

from univention.scim.client.authentication import AuthMethod, get_auth


class ScimConsumerSettings(BaseSettings):
    scim_server_base_url: str
    scim_auth_method: AuthMethod
    health_check_enabled: bool = True
    # Attribute in the UDM user object that controls replication to the SCIM API.
    # If it is truthy , the object will be transfered to SCIM.
    scim_user_filter_attribute: str | None = None
    external_id_user_mapping: str | None = None
    external_id_group_mapping: str | None = None
    _auth: httpx.Auth | None = PrivateAttr(default=None)

    @property
    def auth(self) -> httpx.Auth | None:
        return self._auth

    @auth.setter
    def auth(self, value: httpx.Auth | None) -> None:
        self._auth = value


def get_scim_consumer_settings() -> ScimConsumerSettings:
    settings = ScimConsumerSettings()
    settings.auth = get_auth(settings.scim_auth_method)
    return settings
