.. SPDX-FileCopyrightText: 2025 Univention GmbH
..
.. SPDX-License-Identifier: AGPL-3.0-only

.. _scim-client-prerquesites:

Prerequisites
=============

Before you install the *SCIM Client*, make sure that you have the following:

#. Helm configured to authenticate to the Kubernetes cluster running Nubus.
   The Kubernetes API must be reachable from the system
   where you run the installation commands.
   Your credentials must allow Helm to install the *SCIM Client* release
   and upgrade the existing Nubus release in the Nubus namespace,
   including access to the chart resources and Helm's release Secrets.

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

For the optional :ref:`deployment status check <scim-client-installation-verify>`,
you also need ``kubectl`` configured for the same cluster
and permission to ``get`` ``deployments`` in the ``apps`` API group
in the Nubus namespace.
