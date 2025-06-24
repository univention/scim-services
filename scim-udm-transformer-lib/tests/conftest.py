# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

import pytest

from univention.scim.server.models.types import GroupWithExtensions, UserWithExtensions
from univention.scim.transformation.udm2scim import UdmToScimMapper


@pytest.fixture
def udm2scim_mapper() -> UdmToScimMapper:
    mapper = UdmToScimMapper(user_type=UserWithExtensions, group_type=GroupWithExtensions)

    return mapper
