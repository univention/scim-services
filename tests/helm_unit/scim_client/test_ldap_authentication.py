# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

from univention.testing.helm.auth_flavors.password_usage import AuthPasswordUsageViaEnv
from univention.testing.helm.auth_flavors.secret_generation import AuthSecretGenerationUser
from univention.testing.helm.auth_flavors.username import AuthUsernameViaConfigMap


class SettingsTestLdapSecret:
    secret_name = "release-name-scim-client-ldap"
    prefix_mapping = {
        "auth.bindDn": "auth.username",
        "ldap.auth": "auth",
    }


class TestChartCreatesLdapSecretAsUser(SettingsTestLdapSecret, AuthSecretGenerationUser):
    pass


class TestScimClientUsesLdapCredentialsByEnv(SettingsTestLdapSecret, AuthPasswordUsageViaEnv):
    sub_path_env_password = "env[?@name=='LDAP_BIND_PASSWORD']"
    workload_name = "release-name-scim-client"


class TestScimClientUsesLdapUsernameViaConfigMap(SettingsTestLdapSecret, AuthUsernameViaConfigMap):
    configmap_name = "release-name-scim-client"
    path_username = "data.LDAP_BIND_DN"
    default_username = "uid=stub,cn=users,dc=univention-organization,dc=intranet"
