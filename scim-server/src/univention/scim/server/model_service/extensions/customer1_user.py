# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

from typing import Annotated

from scim2_models import ComplexAttribute, Extension, Required


class GuardianMember(ComplexAttribute):
    value: str | None = None
    type: str | None = None


class Customer1User(Extension):
    schemas: Annotated[list[str], Required.true] = ["urn:ietf:params:scim:schemas:extension:DapUser:2.0:User"]

    primary_org_unit: str | None = None
    secondary_org_units: list[str] | None = None
