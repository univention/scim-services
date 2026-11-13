#!/bin/bash
# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2026 Univention GmbH

set -e

for profile in test-against-reference-server test-against-univention-server; do
  (
    echo "Running ${profile} tests"
    function cleanup {
      docker compose logs scim-server-reference > ../../scim-server.logs
      docker compose logs udm-rest-api > ../../udm-rest-api.logs
      docker compose logs udm-listener > ../../udm-listener.logs
      docker compose logs provisioning-api > ../../provisioning-api.logs
      docker compose --profile ${profile} down --volumes --remove-orphans
    }
    trap cleanup EXIT

    cd scim-client/tests/

    docker compose --profile ${profile} pull
    if [ "${profile}" == "test" ]; then
      docker compose --profile ${profile} build scim-server-reference
    else
      docker compose --profile ${profile} build scim-server-univention
    fi
    docker compose build ${profile}
    docker compose run --name scim-client-${profile} --rm -ti ${profile} $@
    cleanup
  )
done
