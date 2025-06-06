#!/bin/sh
# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH


cd scim-consumer
uv run pytest
uv run coverage xml --ignore-errors
