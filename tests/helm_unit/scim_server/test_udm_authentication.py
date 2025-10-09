# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

from univention.testing.helm.auth_flavors.password_usage import AuthPasswordUsageViaEnv
from univention.testing.helm.auth_flavors.secret_generation import AuthSecretGenerationOwner
from univention.testing.helm.auth_flavors.username import AuthUsernameViaEnv


class SettingsTestUdmSecret:
    secret_name = "release-name-scim-server-udm-secret"
    prefix_mapping = {
        "udm.auth": "auth",
    }
    workload_name = "release-name-scim-server"

    # for AuthUsernameViaEnv
    default_username = "Administrator"


class TestChartCreatesUdmSecretAsUser(SettingsTestUdmSecret, AuthSecretGenerationOwner):
    derived_password = "00fc6a413808ae50b3026ee107d95367526a28fe"


class TestScimServerUsesUdmCredentialsByEnv(SettingsTestUdmSecret, AuthPasswordUsageViaEnv):
    sub_path_env_password = "env[?@name=='UDM_PASSWORD']"


class TestScimServerUsesUdmUsernameViaEnv(SettingsTestUdmSecret, AuthUsernameViaEnv):
    sub_path_env_username = "env[?@name=='UDM_USERNAME']"


class TestScimServerInitContainerUsesUdmCredentialsByEnv_WaitForUdm(SettingsTestUdmSecret, AuthPasswordUsageViaEnv):
    sub_path_env_password = "env[?@name=='UDM_API_PASSWORD']"
    path_container = "..spec.template.spec.initContainers[?@.name=='wait-for-udm']"


class TestScimServerInitContainerUsesUdmUsernameViaEnv_WaitForUdm(SettingsTestUdmSecret, AuthUsernameViaEnv):
    sub_path_env_username = "env[?@name=='UDM_API_USERNAME']"
    path_container = "..spec.template.spec.initContainers[?@.name=='wait-for-udm']"
