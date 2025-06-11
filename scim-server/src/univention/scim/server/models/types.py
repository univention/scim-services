# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

from typing import Union

from scim2_models import EnterpriseUser, Group

from univention.scim.server.models.extensions.customer1_user import Customer1User
from univention.scim.server.models.extensions.univention_group import UniventionGroup
from univention.scim.server.models.extensions.univention_user import UniventionUser
from univention.scim.server.models.user import User


# Union is the scim2-models way of defining multiple extensions,
# ignore ruff UP007 we need the type Union otherwise underlaying scim2-model will fail
UserWithExtensions = User[Union[EnterpriseUser, UniventionUser, Customer1User]]  # noqa: UP007
GroupWithExtensions = Group[UniventionGroup]
