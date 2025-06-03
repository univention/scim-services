# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

from univention.testing.helm.serviceaccount import ServiceAccount


class TestServiceAccount(ServiceAccount):
    template_file = "templates/serviceaccount.yaml"
