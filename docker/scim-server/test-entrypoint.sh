#!/bin/bash
# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH


cd scim-server
uv sync

uv run pytest tests/ $@
uv run coverage xml --ignore-errors
