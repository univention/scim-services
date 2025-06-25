# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

import json

import pytest
from pytest_helm.helm import Helm
from pytest_helm.utils import load_yaml
from univention.testing.helm.base import Annotations, Labels, Namespace
from univention.testing.helm.secret import SecretPasswords


class TestScimServer(SecretPasswords):
    template_file = "templates/secret-scim.yaml"

    def values(self, localpart: dict) -> dict:
        return {"scimServer": localpart}

    @pytest.mark.skip("Not relevant for secrets with password generation")
    def test_auth_plain_values_password_is_required(self): ...

    @pytest.mark.skip("Not relevant for secrets with password generation")
    def test_auth_plain_values_password_has_no_default_value(self): ...

    @pytest.mark.skip("Not relevant for secrets with password generation")
    def test_global_secrets_keep_is_ignored(self): ...


class TestNubusProvisioningSubscription(Annotations, Labels, Namespace):
    template_file = "templates/secret-provisioning.yaml"
    manifest_name = "release-name-scim-consumer-provisioning"
    secret_key = "registration"

    def values(self, localpart: dict) -> dict:
        return {"provisioningApi": localpart}

    def helm_template_file(
        self,
        helm: Helm,
        chart,
        values: dict,
        template_file: str,
        helm_args: list[str] | None = None,
    ) -> dict:
        assert template_file
        result = helm.helm_template(chart=chart, values=values, template_file=template_file, helm_args=helm_args)
        try:
            secret = result.get_resource(kind="Secret", name=self.manifest_name)
        except LookupError:
            return {}
        return secret

    def get_password(self, result):
        result = json.loads(result["stringData"][self.secret_key])["password"]
        return result

    def test_can_be_deployed_multiple_times(self, helm, chart_path):
        nextcloud_values = load_yaml("""
        scimConsumer:
            config:
                prefill: false
                groupSync: false
        """)

        # Disable groups/group topic for one of the subscriptions
        openproject_manifest = helm.helm_template(
            chart=chart_path, template_file=self.template_file, release_name="openproject"
        )
        openproject_secret = openproject_manifest.get_resource(
            kind="Secret", name="openproject-scim-consumer-provisioning"
        )
        openproject = json.loads(openproject_secret["stringData"]["registration"])

        nextcloud_manifest = helm.helm_template(
            chart=chart_path, values=nextcloud_values, template_file=self.template_file, release_name="nextcloud"
        )
        nextcloud_secret = nextcloud_manifest.get_resource(kind="Secret", name="nextcloud-scim-consumer-provisioning")
        nextcloud = json.loads(nextcloud_secret["stringData"]["registration"])

        assert openproject["name"] != nextcloud["name"]
        assert openproject["password"] != nextcloud["password"]
        assert openproject["request_prefill"] != nextcloud["request_prefill"]
        # Disable groups/group topic for one of the subscriptions
        assert openproject["realms_topics"] != nextcloud["realms_topics"]

    def test_auth_plain_values_generate_secret(self, helm, chart_path):
        values = self.values(
            load_yaml("""
            auth:
              password: "stub-password"
        """),
        )
        result = self.helm_template_file(helm, chart_path, values, self.template_file)
        assert self.get_password(result) == "stub-password"

    def test_auth_plain_values_password_is_not_templated(self, helm, chart_path):
        values = self.values(
            load_yaml("""
            auth:
              password: "{{ value }}"
        """),
        )
        result = self.helm_template_file(helm, chart_path, values, self.template_file)
        assert self.get_password(result) == "{{ value }}"

    def test_auth_existing_secret_does_not_generate_a_secret(
        self,
        helm,
        chart_path,
    ):
        values = self.values(
            load_yaml(
                """
            auth:
              existingSecret:
                name: "stub-secret-name"
        """,
            ),
        )
        result = self.helm_template_file(helm, chart_path, values, self.template_file)
        assert result == {}

    def test_auth_existing_secret_does_not_require_plain_password(
        self,
        helm,
        chart_path,
    ):
        values = self.values(
            load_yaml(
                """
            auth:
              password: null
              existingSecret:
                name: "stub-secret-name"
        """,
            ),
        )
        result = self.helm_template_file(helm, chart_path, values, self.template_file)
        assert result == {}

    def test_auth_existing_secret_has_precedence(self, helm, chart_path):
        values = self.values(
            load_yaml(
                """
            auth:
              password: stub-plain-password
              existingSecret:
                name: "stub-secret-name"
                keyMapping:
                  password: "stub_password_key"
        """,
            ),
        )
        result = self.helm_template_file(helm, chart_path, values, self.template_file)
        assert result == {}
