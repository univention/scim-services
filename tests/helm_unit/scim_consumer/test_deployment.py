# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

import pytest
from univention.testing.helm.container import ContainerEnvVarSecret
from univention.testing.helm.deployment import Deployment


class TestDeployment(Deployment):
    template_file = "templates/deployment.yaml"


@pytest.mark.parametrize(
    "key, env_var",
    [
        ("scimServer", "SCIM_API_PASSWORD"),
        ("nubusProvisioning", "PROVISIONING_API_PASSWORD"),
    ],
)
class TestMainContainer(ContainerEnvVarSecret):
    template_file = "templates/deployment.yaml"
    container_name = "scim-consumer"


@pytest.mark.parametrize(
    "key, env_var",
    [
        ("ldap", "LDAP_BIND_PASSWORD"),
    ],
)
class TestMainContainerLdapPassword(ContainerEnvVarSecret):
    template_file = "templates/deployment.yaml"
    container_name = "scim-consumer"

    @pytest.mark.skip("Not relevant for secrets with password generation")
    def test_auth_disabling_existing_secret(self, key, env_var): ...
