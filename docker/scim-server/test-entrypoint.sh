#!/bin/sh
# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH


cd scim-server
uv sync
uv run pytest -lv $@ tests/unit/
uv run pytest -lv $@ tests/e2e/
uv run pytest -lv $@ tests/middlewares/
