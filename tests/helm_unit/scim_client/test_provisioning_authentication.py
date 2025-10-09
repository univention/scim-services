# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

import pytest
from univention.testing.helm.auth_flavors.password_usage import AuthPasswordUsageViaEnv
from univention.testing.helm.auth_flavors.secret_generation import AuthSecretGenerationOwner
from univention.testing.helm.auth_flavors.username import AuthUsernameViaConfigMap


class SettingsTestProvisioningSecret:
    secret_name = "release-name-scim-client-provisioning"
    prefix_mapping = {
        "provisioningApi.auth": "auth",
    }


class TestChartCreatesProvisioningSecretAsUser(SettingsTestProvisioningSecret, AuthSecretGenerationOwner):
    derived_password = "9885dbfd09545ec0e87d07c3cd2dc15e0b412e52"


class TestScimClientUsesProvisioningCredentialsByEnv(SettingsTestProvisioningSecret, AuthPasswordUsageViaEnv):
    sub_path_env_password = "env[?@name=='PROVISIONING_API_PASSWORD']"
    workload_name = "release-name-scim-client"


class TestScimClientUsesProvisioningUsernameViaConfigMap(SettingsTestProvisioningSecret, AuthUsernameViaConfigMap):
    configmap_name = "release-name-scim-client"
    path_username = "data.PROVISIONING_API_USERNAME"
    default_username = "release-name-scim-client"

    @pytest.mark.skip("Configmap creates default username automatically")
    def test_auth_username_is_required(self, chart): ...
