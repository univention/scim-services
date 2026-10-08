# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

from scim2_models import URN, ComplexAttribute, Extension


class GuardianMember(ComplexAttribute):
    value: str | None = None
    type: str | None = None


class Customer1User(Extension):
    __schema__ = URN("urn:ietf:params:scim:schemas:extension:UniventionUser:2.0:User")

    primary_org_unit: str | None = None
    secondary_org_units: list[str] | None = None
