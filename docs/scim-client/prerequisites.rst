.. SPDX-FileCopyrightText: 2025 Univention GmbH
..
.. SPDX-License-Identifier: AGPL-3.0-only

.. _conf-scim-client-installation-prerequisites:

Prerequisites
=============

Before you install the *SCIM Client*,
you need to ensure the following prerequisites:

#. A Nubus for Kubernetes deployment.
   For installation, see :external+uv-nubus-kubernetes-operation:ref:`nubus-deployment`.

#. A SCIM-compliant service provider, called the SCIM target on this page.

#. Connection details for the SCIM target,
   including endpoint URL and authentication credentials.

#. A separate PostgreSQL database for each *SCIM Client*
   and a dedicated database user with permission to create and modify its tables.
   See :ref:`conf-scim-client-configuration-database`.
