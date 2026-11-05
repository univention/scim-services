.. SPDX-FileCopyrightText: 2025 Univention GmbH
..
.. SPDX-License-Identifier: AGPL-3.0-only

.. _conf-scim-client-deployment:

Deployment
==========

You deploy the *SCIM Client* and Nubus for Kubernetes through independent Helm Charts.
After you have configured their respective values files—in the example on this page
the :file:`scim-client-values.yaml` file and the :file:`nubus-values.yaml` file—you
can deploy or upgrade the installations,
as shown in :numref:`conf-scim-client-deployment-listing`.

Although you deploy the *SCIM Client* and Nubus for Kubernetes independently,
their configuration relates to each other.
For example, the ``provisioningApi`` and ``ldap`` sections in the *SCIM Client*\'s :file:`scim-client-values.yaml` values file
must correctly point to Nubus for Kubernetes.
Likewise, the provisioning subscription in the Nubus :file:`nubus-values.yaml` values file must match the *SCIM
Client* values.

.. code-block:: console
   :caption: Deploy *SCIM Client* and update Nubus for Kubernetes
   :name: conf-scim-client-deployment-listing

   $ export NUBUS_NAMESPACE="<Your Nubus for Kubernetes namespace>"
   $ export RELEASE_NAME_FOR_NUBUS="<The release name of your Nubus installation>"

   $ helm upgrade \
       --install \
       scim-client \
       --namespace "$NUBUS_NAMESPACE" \
       oci://artifacts.software-univention.de/nubus/charts/scim-client \
       --values scim-client-values.yaml

   $ helm upgrade \
       --install \
       "$RELEASE_NAME_FOR_NUBUS" \
       --namespace "$NUBUS_NAMESPACE" \
       oci://artifacts.software-univention.de/nubus/charts/nubus \
       --values nubus-values.yaml
