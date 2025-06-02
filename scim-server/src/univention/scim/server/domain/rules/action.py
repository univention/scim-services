# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

from enum import Enum


class Action(Enum):
    Create = (1,)
    Update = (2,)
    Patch = 3
