.. SPDX-FileCopyrightText: 2025 Univention GmbH
..
.. SPDX-License-Identifier: AGPL-3.0-only

.. _conf-scim-client-installation:

Installation
============

This section describes how to install the *SCIM Client* through Helm.

.. _conf-scim-client-installation-helm:

Installation through Helm
-------------------------

To install the *SCIM Client* through Helm,
use the commands in :numref:`conf-scim-client-installation-helm-listing`.
For the configuration of the *SCIM Client*,
see :ref:`conf-scim-client-configuration`.

You need to install the *SCIM Client* in the same namespace as Nubus for Kubernetes.
The reason is
that the *SCIM Client* needs internal access to the *Provisioning API* and the *LDAP Server*.

.. code-block:: console
   :caption: Install the *SCIM Client* through Helm
   :name: conf-scim-client-installation-helm-listing

   $ export NUBUS_NAMESPACE="<Your Nubus for Kubernetes namespace>"
   $ helm install \
       scim-client \
       --namespace "$NUBUS_NAMESPACE" \
       oci://artifacts.software-univention.de/nubus/charts/scim-client \
       --values values.yaml
