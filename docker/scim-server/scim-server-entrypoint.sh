#!/bin/sh
# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH


set -e

if [ "${ADD_LDAP_ATTRIBUTES}" != "" ]; then
    echo "Creating required LDAP extended attributes"
    /create_ldap_attributes.py
fi

scim-server
