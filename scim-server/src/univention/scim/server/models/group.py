# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

from typing import Annotated

from scim2_models import (
    AnyExtension,
    Group as ScimGroup,
    Required,
)


class Group(ScimGroup[AnyExtension]):
    # UDM requires a name so mark it as required also in the scim model
    display_name: Annotated[str | None, Required.true] = None
