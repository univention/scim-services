#!/bin/bash
# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH


(
  cd scim-server/tests/

  docker compose pull
  docker compose build test
  docker compose run --rm -ti test $@
  docker compose down --volumes
)
