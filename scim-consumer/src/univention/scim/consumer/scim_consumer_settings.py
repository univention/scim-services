# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

from pydantic_settings import BaseSettings


class ScimConsumerSettings(BaseSettings):
    scim_server_base_url: str
    scim_oidc_authentication: bool
    health_check_enabled: bool = True
    # Attribute in the UDM user object that controls replication to the SCIM API.
    # If it is truthy , the object will be transfered to SCIM.
    scim_user_filter_attribute: str | None = None
    external_id_user_mapping: str | None = None
    external_id_group_mapping: str | None = None
