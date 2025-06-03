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
        ("nubusProvisioning.connection.url", "PROVISIONING_API_BASE_URL"),
        ("scimServer.auth.username", "SCIM_API_USERNAME"),
        ("nubusProvisioning.connection.maxAcknowledgementRetries", "MAX_ACKNOWLEDGEMENT_RETRIES"),
    ],
)
class TestRequiredConfigMapEnv(RequiredEnvVariables):
    template_file = "templates/configmap.yaml"


@pytest.mark.parametrize(
    "key, env_var",
    [
        ("nubusProvisioning.auth.username", "PROVISIONING_API_USERNAME"),
    ],
)
class TestDefaultEnvVariables(DefaultEnvVariables):
    template_file = "templates/configmap.yaml"
