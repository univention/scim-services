# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

from univention.testing.helm.auth_flavors.password_usage import AuthPasswordUsageViaEnv
from univention.testing.helm.auth_flavors.secret_generation import AuthSecretGenerationUser
from univention.testing.helm.auth_flavors.username import AuthUsernameViaConfigMap


class SettingsTestScimServerSecret:
    secret_name = "release-name-scim-client-scim-server"
    prefix_mapping = {
        "auth.clientId": "auth.username",
        "scimServer.auth": "auth",
    }


class TestChartCreatesScimServerSecretAsUser(SettingsTestScimServerSecret, AuthSecretGenerationUser):
    pass


class TestScimClientUsesScimServerCredentialsByEnv(SettingsTestScimServerSecret, AuthPasswordUsageViaEnv):
    sub_path_env_password = "env[?@name=='SCIM_CLIENT_SECRET']"
    workload_name = "release-name-scim-client"


class TestScimClientUsesScimServerUsernameViaConfigMap(SettingsTestScimServerSecret, AuthUsernameViaConfigMap):
    configmap_name = "release-name-scim-client"
    path_username = "data.SCIM_CLIENT_ID"
    default_username = "stub-scim-api-username"
