#!/usr/bin/env bash
# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2026 Univention GmbH

# Update the SCIM Client Helm Chart values reference.
#
# Run from the repository root in the Sphinx base container image:
#
#   docs/scim-client/update-scim-client-values-reference.sh 0.55.4
#
# Alternatively, set the version through the environment:
#
#   SCIM_CLIENT_HELM_VERSION=0.55.4 \
#     docs/scim-client/update-scim-client-values-reference.sh
#
# The script downloads the SCIM Client Helm Chart, generates the Frigate values
# reference, and writes:
#
#   docs/scim-client/reference-values-scim-client.txt

set -euo pipefail

SCIM_CLIENT_HELM_VERSION="${1:-${SCIM_CLIENT_HELM_VERSION:-}}"

if [[ -z "$SCIM_CLIENT_HELM_VERSION" ]]; then
  printf 'Usage: %s <SCIM_CLIENT_HELM_VERSION>\n' "$0" >&2
  printf 'Or set SCIM_CLIENT_HELM_VERSION in the environment.\n' >&2
  exit 2
fi

output_file="docs/scim-client/reference-values-scim-client.txt"
frigate_template="docs/.frigate-scim-client"

if [[ ! -f "$frigate_template" || ! -d "docs/scim-client" ]]; then
  printf 'Run this script from the repository root.\n' >&2
  exit 2
fi

tmpdir="$(mktemp -d)"
trap 'rm -rf "$tmpdir"' EXIT

helm pull \
  oci://artifacts.software-univention.de/nubus/charts/scim-client \
  --version "$SCIM_CLIENT_HELM_VERSION" \
  --destination "$tmpdir"

tar -xzf "$tmpdir/scim-client-$SCIM_CLIENT_HELM_VERSION.tgz" -C "$tmpdir"
ln -s "$PWD/$frigate_template" "$tmpdir/scim-client/.frigate"

frigate gen \
  --output-format rst \
  --no-credits \
  --helm-docs \
  --skip-helm-update \
  "$tmpdir/scim-client" >"$output_file"

if ! grep -Fq ":Version: \`\`$SCIM_CLIENT_HELM_VERSION\`\`" "$output_file"; then
  printf 'Generated reference does not contain expected version: %s\n' "$SCIM_CLIENT_HELM_VERSION" >&2
  exit 1
fi

printf 'Updated %s for SCIM Client Helm Chart version %s\n' "$output_file" "$SCIM_CLIENT_HELM_VERSION"
