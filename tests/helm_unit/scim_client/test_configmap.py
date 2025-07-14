# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

import pytest
from univention.testing.helm.configmap import (
    ConfigMap,
    DefaultEnvVariables,
    RequiredEnvVariables,
)


class TestConfigMap(ConfigMap):
    template_file = "templates/configmap.yaml"


@pytest.mark.parametrize(
    "key, env_var",
    [
        ("scimConsumer.config.logLevel", "LOG_LEVEL"),
        ("provisioningApi.connection.url", "PROVISIONING_API_BASE_URL"),
        ("provisioningApi.config.maxAcknowledgementRetries", "MAX_ACKNOWLEDGEMENT_RETRIES"),
        ("scimServer.connection.url", "SCIM_SERVER_BASE_URL"),
        ("ldap.connection.host", "LDAP_HOST"),
        ("ldap.auth.bindDn", "LDAP_BIND_DN"),
        ("scimServer.auth.clientId", "SCIM_CLIENT_ID"),
        ("scimServer.auth.oidcTokenUrl", "SCIM_OIDC_TOKEN_URL"),
        ("scimServer.auth.enabled", "SCIM_OIDC_AUTHENTICATION"),
    ],
)
class TestRequiredConfigMapEnv(RequiredEnvVariables):
    template_file = "templates/configmap.yaml"


@pytest.mark.parametrize(
    "key, env_var",
    [
        ("provisioningApi.auth.username", "PROVISIONING_API_USERNAME"),
    ],
)
class TestDefaultEnvVariables(DefaultEnvVariables):
    template_file = "templates/configmap.yaml"
