# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

from scim2_models import EnterpriseUser

from univention.scim.server.models.extensions.customer1_user import Customer1User
from univention.scim.server.models.extensions.univention_group import UniventionGroup
from univention.scim.server.models.extensions.univention_user import UniventionUser
from univention.scim.server.models.group import Group
from univention.scim.server.models.user import User


UserWithExtensions = User[EnterpriseUser | UniventionUser | Customer1User]
GroupWithExtensions = Group[UniventionGroup]
