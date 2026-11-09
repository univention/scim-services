.. SPDX-FileCopyrightText: 2025 Univention GmbH
..
.. SPDX-License-Identifier: AGPL-3.0-only

.. _conf-scim-client-installation-prerequisites:

Prerequisites
=============

Before you install the *SCIM Client*, make sure that you have the following:

#. A Nubus for Kubernetes deployment.
   For installation,
   see :external+uv-nubus-kubernetes-operation:ref:`nubus-deployment`
   in :cite:t:`uv-nubus-kubernetes-operation`.

#. An external application that provides a SCIM interface, referred to as the SCIM target in this manual.
   For the supported schemas, see :ref:`conf-scim-client-schemas`.

#. Connection details for the SCIM target,
   including its endpoint URL and authentication credentials.

#. A separate PostgreSQL database for each *SCIM Client*
   and a dedicated database user with permission to create and modify its tables.
   For more information, see :ref:`conf-scim-client-configuration-database`.

#. If you enable group synchronization,
   internal network access from the *SCIM Client* to the *LDAP Server*.
   The client uses LDAP to resolve group member distinguished names.

   The Helm Chart requires LDAP connection and authentication settings
   even if you don't enable group synchronization.
   For the required settings, see :ref:`scim-client-configuration-mandatory`.

.. _scim-client-installation-overview:

Installation overview
---------------------

The *SCIM Client* has its own Helm Chart, separate from your existing Nubus deployment.
Before you install the client, prepare the settings for both charts in Helm *values files*.
Helm uses these files when installing or updating the components.

The installation consists of the following steps:

#. Prepare the :file:`scim-client-values.yaml` file with connection and authentication details for the following systems:

   * *SCIM target*
   * *Provisioning API*
   * *LDAP Server*
   * PostgreSQL database

   For more information, see :ref:`conf-scim-client-configuration`.

#. Add the subscription configuration to the :file:`nubus-values.yaml` file for your existing Nubus deployment
   so that the client can receive user and user group changes.
   For more information, see :ref:`conf-scim-client-provisioning`.

#. Install the client first, then update Nubus to register the subscription,
   as described in :ref:`conf-scim-client-installation`.
   The commands in those instructions apply the values files prepared in the previous steps.
