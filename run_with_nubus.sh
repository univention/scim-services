#!/bin/bash
# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH


client_secret="$(kubectl get secret nubus-scim-server-keycloak-client-secret -o jsonpath='{.data.oauthAdapterM2mSecret}' | base64 --decode)"
client_id="$(kubectl get configmap nubus-scim-server-env -o jsonpath='{.data.AUTHENTICATOR_CLIENT_ID}')"
udm_url="https://$(kubectl get ingress nubus-udm-rest-api --no-headers | awk '{ print $3}')/univention/udm"
udm_username="$(kubectl get secret nubus-scim-server-udm-secret -o jsonpath='{.data.username}' | base64 --decode)"
udm_password="$(kubectl get secret nubus-scim-server-udm-secret -o jsonpath='{.data.password}' | base64 --decode)"
scim_api_group_dn="$(kubectl get configmap nubus-scim-server-env -o jsonpath='{.data.AUTHENTICATOR_ALLOW_GROUP_DN}')"
idp_config_url="$(kubectl get configmap nubus-scim-server-env -o jsonpath='{.data.AUTHENTICATOR_IDP_OPENID_CONFIGURATION_URL}')"

echo "Client secret: ${client_secret}"
echo "Client ID: ${client_id}"
echo "UDM URL: ${udm_url}"
echo "UDM username: ${udm_username}"
echo "UDM password: ${udm_password}"
echo "SCIM allowed groupd DN: ${scim_api_group_dn}"
echo "IDP config URL: ${idp_config_url}"

(
  cd scim-server && \
    LOG_LEVEL="DEBUG" \
    AUTHENTICATOR_CLIENT_SECRET="${client_secret}" \
    AUTHENTICATOR_CLIENT_ID="${client_id}" \
    AUTHENTICATOR_ALLOW_GROUP_DN="${scim_api_group_dn}" \
    UDM_URL="${udm_url}" \
    UDM_USERNAME="${udm_username}" \
    UDM_PASSWORD="${udm_password}" \
    AUTHENTICATOR_IDP_OPENID_CONFIGURATION_URL="${idp_config_url}" \
    HOST="http://127.0.0.1:8000" \
    uv run uvicorn --reload src.univention.scim.server.main:app
)
