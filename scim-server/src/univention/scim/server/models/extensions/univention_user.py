# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

from scim2_models import URN, Extension


class UniventionUser(Extension):
    __schema__ = URN("urn:ietf:params:scim:schemas:extension:Univention:1.0:User")

    description: str | None = None
    password_recovery_email: str | None = None
