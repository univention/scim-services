# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

from typing import Annotated

from scim2_models import Extension, Required


class UniventionUser(Extension):
    schemas: Annotated[list[str], Required.true] = ["urn:ietf:params:scim:schemas:extension:Univention:1.0:User"]

    description: str | None = None
    password_recovery_email: str | None = None
