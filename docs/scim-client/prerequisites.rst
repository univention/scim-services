.. SPDX-FileCopyrightText: 2025 Univention GmbH
..
.. SPDX-License-Identifier: AGPL-3.0-only

.. _conf-scim-client-installation-prerequisites:

Prerequisites
=============

Before you install the *SCIM Client*, make sure that you have the following:

#. A Nubus for Kubernetes deployment.
   For installation, see :external+uv-nubus-kubernetes-operation:ref:`nubus-deployment`.

#. An external application that provides a SCIM interface, referred to as the SCIM target in this manual.
   See :ref:`conf-scim-client-schemas` for the supported schemas.

#. Connection details for the SCIM target, including its endpoint URL and authentication credentials.

#. A separate PostgreSQL database for each *SCIM Client* and a dedicated database user with permission to create and modify its tables.
   See :ref:`conf-scim-client-configuration-database`.

.. _conf-scim-client-installation-overview:

Installation overview
---------------------

The *SCIM Client* has its own Helm Chart, separate from your existing Nubus deployment.
Before installing the client, prepare the settings for both charts in Helm *values files*.
Helm uses these files when installing or updating the components.

The installation consists of the following steps:

#. Prepare :file:`scim-client-values.yaml` with the connection details and credentials for Nubus, the SCIM target, and the PostgreSQL database.
   See :ref:`conf-scim-client-configuration`.

#. Add the subscription configuration to the :file:`nubus-values.yaml` file for your existing Nubus deployment so that the client can receive user and user group changes.
   See :ref:`conf-scim-client-provisioning`.

#. Install the client first, then update Nubus to register the subscription, as described in :ref:`conf-scim-client-installation`.
   These commands apply the values files prepared in the previous steps.
