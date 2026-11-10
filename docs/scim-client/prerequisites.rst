.. SPDX-FileCopyrightText: 2025 Univention GmbH
..
.. SPDX-License-Identifier: AGPL-3.0-only

.. _scim-client-prerquesites:

Prerequisites
=============

Before you install the *SCIM Client*, make sure that you have the following:

#. A Nubus for Kubernetes deployment.
   For installation,
   see :external+uv-nubus-kubernetes-operation:ref:`nubus-deployment`
   in :cite:t:`uv-nubus-kubernetes-operation`.

#. An external application that provides a SCIM interface, referred to as the SCIM target in this manual.
   For the supported schemas, see :ref:`scim-client-schemas`.

#. Connection details for the SCIM target,
   including its endpoint URL and authentication credentials.

#. A separate PostgreSQL database for each *SCIM Client*
   and a dedicated database user with permission to create and modify its tables.
   For more information, see :ref:`scim-client-configuration-database`.

#. If you enable group synchronization,
   internal network access from the *SCIM Client* to the *LDAP Server*.
   The client uses LDAP to resolve group member distinguished names.

   The Helm Chart requires LDAP connection and authentication settings
   even if you don't enable group synchronization.
   For the required settings, see :ref:`scim-client-configuration-mandatory`.
