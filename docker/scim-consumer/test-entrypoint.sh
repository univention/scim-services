#!/bin/sh
# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

set -x

# Run pytest and coverage from /app to get proper paths in coverage report.

# coverage seems to ignore "pytest --config-file=" and "coverage --rcfile=", so passing in everything explicitly.

uv sync --directory scim-consumer
uv run pytest --config-file=/app/scim-consumer/pyproject.toml --cov-config=/app/scim-consumer/pyproject.toml -p no:cacheprovider scim-consumer/tests
uv run coverage xml --rcfile=/app/scim-consumer/pyproject.toml --ignore-errors --data-file=/tmp/scim-coverage -o /tmp/scim-coverage.xml
