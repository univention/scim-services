#!/bin/bash
# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

set -e

(
  function cleanup {
    docker compose --profile test down --volumes --remove-orphans
  }
  trap cleanup EXIT

  cd scim-consumer/tests/

  docker compose --profile test pull
  docker compose --profile test build scim-dev-server
  docker compose build test
  docker compose run --rm -ti test $@
)
