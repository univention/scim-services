.. SPDX-FileCopyrightText: 2025 Univention GmbH
..
.. SPDX-License-Identifier: AGPL-3.0-only

.. _scim-client-installation:

Installation
============

This page describes how to install and update the *SCIM Client*.
Before you start,
make sure that you completed the following sections:

* :ref:`scim-client-prerquesites`
* :ref:`scim-client-configuration`
* :ref:`scim-client-provisioning`

The *SCIM Client* and Nubus for Kubernetes use separate Helm releases.
Install the *SCIM Client* in the same Kubernetes namespace
as Nubus for Kubernetes.

Use the :file:`scim-client-values.yaml` and :file:`nubus-values.yaml` files
prepared in the previous sections.
For an example with multiple SCIM targets,
see :ref:`scim-client-provisioning-multiple`.

The *SCIM Client* has its own Helm Chart, separate from your existing Nubus deployment.
Before you install the client, prepare the settings for both charts in Helm Chart values files.
Helm uses these files when installing or updating the components.

The installation consists of the following steps:

#. Prepare the :file:`scim-client-values.yaml` file with connection and authentication details for the following systems:

   * *SCIM target*
   * *Provisioning API*
   * *LDAP Server*
   * PostgreSQL database

   For the required settings, see :ref:`scim-client-configuration-mandatory`.

#. Add the subscription configuration to the :file:`nubus-values.yaml` file for your existing Nubus deployment
   so that the client can receive user changes.
   If you enable group synchronization,
   the client can also receive user group changes.
   For more information, see :ref:`scim-client-provisioning`.

#. Install the client first, then update Nubus to register the subscription,
   as described in :ref:`scim-client-installation-helm`.
   The commands in those instructions apply the values files prepared in the previous steps.

.. _scim-client-installation-helm:

Installation through Helm
-------------------------

To install the *SCIM Client* through Helm, use the following steps.

#. Prepare the environment variables with the commands in :numref:`scim-client-deployment-prepare-env-listing`:

   * For your existing Nubus for Kubernetes deployment,
     set the following environment variables to their respective values:

     :``NUBUS_NAMESPACE``: the namespace
     :``RELEASE_NAME_FOR_NUBUS``: the Helm release name
     :``NUBUS_HELM_VERSION``: the Helm Chart version

   * Set ``SCIM_CLIENT_HELM_VERSION`` to the version of the *SCIM Client* Helm Chart
     that you want to install.

   .. tip::

      You can find the installed chart version in the ``CHART`` column of
      :command:`helm list --namespace <namespace>`.

      When you use the same Nubus Helm Chart version,
      Helm applies the subscription configuration without upgrading Nubus to a different version.

   .. code-block:: console
      :caption: Prepare environment variables for the installation
      :name: scim-client-deployment-prepare-env-listing

      $ export NUBUS_NAMESPACE="<Your Nubus for Kubernetes namespace>"
      $ export RELEASE_NAME_FOR_NUBUS="<The release name of your Nubus installation>"
      $ export SCIM_CLIENT_HELM_VERSION="<The SCIM Client Helm Chart version to install>"
      $ export NUBUS_HELM_VERSION="<The Helm Chart version of your Nubus installation>"

#. To install or update the *SCIM Client*,
   run the commands in :numref:`scim-client-deployment-install-scim-client-listing`.

   .. code-block:: console
      :caption: Install or update the *SCIM Client*
      :name: scim-client-deployment-install-scim-client-listing

      $ helm upgrade \
          --install \
          scim-client \
          --namespace "$NUBUS_NAMESPACE" \
          oci://artifacts.software-univention.de/nubus/charts/scim-client \
          --version "$SCIM_CLIENT_HELM_VERSION" \
          --values scim-client-values.yaml

#. To register the subscription in Nubus for Kubernetes,
   run the commands in :numref:`scim-client-deployment-subscription-listing`.

   If you don't configure an existing provisioning secret,
   the client chart creates the registration secret needed for the Nubus update.
   The ``--install`` option installs Nubus
   if the specified Nubus Helm release doesn't exist.

   .. important::

      If your Nubus deployment uses additional values files,
      repeat ``--values`` for each file,
      for example ``--values nubus-values.yaml --values prod_values.yaml``.
      Keep the files in the same order.

   .. code-block:: console
      :caption: Update Nubus and register the subscription
      :name: scim-client-deployment-subscription-listing

      $ helm upgrade \
          --install \
          "$RELEASE_NAME_FOR_NUBUS" \
          --namespace "$NUBUS_NAMESPACE" \
          oci://artifacts.software-univention.de/nubus/charts/nubus \
          --version "$NUBUS_HELM_VERSION" \
          --values nubus-values.yaml

.. _scim-client-installation-verify:

Verify deployment status
------------------------

To verify the deployment status of the *SCIM Client*,
run the command in :numref:`scim-client-installation-verification-listing`.

Expect ``READY`` to show ``1/1`` and ``AVAILABLE`` to show ``1``.
This confirms that Kubernetes reports an available client instance.
It doesn't verify data synchronization with the *SCIM target*.

The client may need a few minutes to start,
for example while Kubernetes downloads the container image.
If ``READY`` shows ``0/1`` or ``AVAILABLE`` shows ``0``,
wait a few minutes and run the command again.
If the client remains unavailable, see :ref:`scim-client-troubleshooting`.

To also verify the synchronization with the *SCIM target*,
follow the optional test-user check in :ref:`scim-client-troubleshooting-verification`.

.. code-block:: console
   :caption: Check the *SCIM Client* deployment (example output)
   :name: scim-client-installation-verification-listing

   $ kubectl get deployment scim-client --namespace "$NUBUS_NAMESPACE"

   NAME          READY   UP-TO-DATE   AVAILABLE   AGE
   scim-client   1/1     1            1           2m
