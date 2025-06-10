# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

from typing import Annotated

from scim2_models import Extension, MultiValuedComplexAttribute, Required


class GuardianMember(MultiValuedComplexAttribute):
    value: str | None = None
    type: str | None = None


class UniventionGroup(Extension):
    schemas: Annotated[list[str], Required.true] = ["urn:ietf:params:scim:schemas:extension:Univention:1.0:Group"]

    description: str | None = None
    member_roles: list[GuardianMember] | None = None
