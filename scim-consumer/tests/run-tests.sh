#!/bin/bash
# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH


clear

docker compose up -d --remove-orphans

sleep 10s

# pytest -v -s test_main.py::test_scim_create_user
pytest -v -s test_main.py

# docker compose down --volumes
