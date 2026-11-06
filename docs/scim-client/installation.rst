.. SPDX-FileCopyrightText: 2025 Univention GmbH
..
.. SPDX-License-Identifier: AGPL-3.0-only

.. _conf-scim-client-installation:

.. _conf-scim-client-deployment:

Installation
============

Install or update the *SCIM Client* and register its provisioning subscription with Nubus for Kubernetes.
The client and Nubus for Kubernetes use separate Helm releases.

Install the *SCIM Client* in the same Kubernetes namespace as Nubus for Kubernetes.
The client needs internal access to the *Provisioning API* and the *LDAP Server*.

Use the :file:`scim-client-values.yaml` and :file:`nubus-values.yaml` files prepared in the previous chapters.
For the preparation steps, see :ref:`conf-scim-client-installation-overview`.

.. _conf-scim-client-installation-helm:

Installation through Helm
-------------------------

Set ``NUBUS_NAMESPACE`` to the namespace of your existing Nubus deployment and ``RELEASE_NAME_FOR_NUBUS`` to its Helm release name.
Set ``SCIM_CLIENT_HELM_VERSION`` to the version of the *SCIM Client* Helm Chart that you want to install.
Set ``NUBUS_HELM_VERSION`` to the Helm Chart version of your existing Nubus deployment.
You can find the installed chart version in the ``CHART`` column of ``helm list --namespace <namespace>``.
Using the same Nubus chart version applies the subscription configuration without upgrading Nubus to a different version.

Run the following commands to install or update the *SCIM Client* first, then register the subscription in Nubus for Kubernetes.
The client chart creates the registration Secret needed for the Nubus update.
The ``--install`` option installs the client if its Helm release doesn't exist yet.

If your Nubus deployment uses additional values files, repeat ``--values`` for each file, for example ``--values nubus-values.yaml --values prod_values.yaml``.
Keep the files in the same order as before.

.. _conf-scim-client-installation-helm-listing:

.. code-block:: console
   :caption: Install or update *SCIM Client* and register its subscription
   :name: conf-scim-client-deployment-listing

   $ export NUBUS_NAMESPACE="<Your Nubus for Kubernetes namespace>"
   $ export RELEASE_NAME_FOR_NUBUS="<The release name of your Nubus installation>"
   $ export SCIM_CLIENT_HELM_VERSION="<The SCIM Client Helm Chart version to install>"
   $ export NUBUS_HELM_VERSION="<The Helm Chart version of your Nubus installation>"

   $ helm upgrade \
       --install \
       scim-client \
       --namespace "$NUBUS_NAMESPACE" \
       oci://artifacts.software-univention.de/nubus/charts/scim-client \
       --version "$SCIM_CLIENT_HELM_VERSION" \
       --values scim-client-values.yaml

   $ helm upgrade \
       --install \
       "$RELEASE_NAME_FOR_NUBUS" \
       --namespace "$NUBUS_NAMESPACE" \
       oci://artifacts.software-univention.de/nubus/charts/nubus \
       --version "$NUBUS_HELM_VERSION" \
       --values nubus-values.yaml

.. _conf-scim-client-installation-verify:

Check deployment status
-----------------------

Optionally, check the Kubernetes deployment status of the *SCIM Client*:

.. code-block:: console
   :caption: Check the *SCIM Client* deployment (example output)
   :name: conf-scim-client-installation-verification-listing

   $ kubectl get deployment scim-client --namespace "$NUBUS_NAMESPACE"

   NAME          READY   UP-TO-DATE   AVAILABLE   AGE
   scim-client   1/1     1            1           2m

Expect ``READY`` to show ``1/1`` and ``AVAILABLE`` to show ``1``.
This confirms that Kubernetes reports an available client instance; it doesn't verify data synchronization with the SCIM target.

The client may need a few minutes to start, for example while Kubernetes downloads the container image.
If ``READY`` shows ``0/1`` or ``AVAILABLE`` shows ``0``, wait a few minutes and run the command again.
If the client remains unavailable, see :ref:`conf-scim-client-troubleshooting`.

To also check synchronization with the SCIM target, follow the optional test-user check in :ref:`conf-scim-client-troubleshooting-verification`.
