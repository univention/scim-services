#!/bin/bash
# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

set -e

for profile in test test-integration; do
  (
    echo "Running ${profile} tests"
    function cleanup {
      docker compose --profile ${profile} down --volumes --remove-orphans
    }
    trap cleanup EXIT

    cd scim-client/tests/

    docker compose --profile ${profile} pull
    if [ "${profile}" == "test" ]; then
      docker compose --profile ${profile} build scim-dev-server
    else
      docker compose --profile ${profile} build scim-server
    fi
    docker compose build ${profile}
    docker compose run --rm -ti ${profile} $@
    cleanup
  )
done
