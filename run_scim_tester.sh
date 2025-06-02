#!/bin/bash
# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH


(
  cd scim-server/tests/

  docker compose pull
  docker compose build scim-server
  docker compose run --rm -ti scim2-tester
  docker compose logs scim-server > ../../scim-server.logs
  docker compose down --volumes
)
