.. SPDX-FileCopyrightText: 2025 Univention GmbH
..
.. SPDX-License-Identifier: AGPL-3.0-only

.. _scim-client-provisioning:

Provisioning subscription
=========================

The *SCIM Client* receives user and user group changes
from the Nubus *Provisioning Service* through a subscription.
Configure a separate client and subscription for each *SCIM target*.
For an example with two targets, see :ref:`scim-client-provisioning-multiple`.

In the setup described in this manual,
the *SCIM Client* Helm Chart creates a secret with the registration data for its subscription.
The Nubus deployment uses this data to register the client with the *Provisioning Service*.

.. _scim-client-provisioning-configure:

Configure a subscription
------------------------

To configure a provisioning subscription,
you need to register the consumer.
Add the configuration in :numref:`scim-client-provisioning-listing`
to the :file:`nubus-values.yaml` file for your existing Nubus deployment.
If :external+uv-nubus-kubernetes-operation:envvar:`nubusProvisioning.registerConsumers.createUsers` already exists,
add the ``scimClient`` entry to it and keep the existing entries.
The configuration references the ``registration`` entry in the ``scim-client-provisioning`` secret.
This entry contains the subscription name, topics, prefill setting, and password.

.. code-block:: yaml
   :caption: Add a subscription for the *SCIM Client* to the Nubus for Kubernetes Helm Chart
   :name: scim-client-provisioning-listing

   nubusProvisioning:
     registerConsumers:
       createUsers:
         scimClient:
           existingSecret:
             name: scim-client-provisioning
             keyMapping:
               registration: "registration"

After you have prepared the Helm Chart files :file:`nubus-values.yaml`
and :file:`scim-client-values.yaml`, continue with :ref:`scim-client-installation`.

.. important::

   Enabling :envvar:`scimClient.config.groupSync` adds the ``groups/group`` topic
   to the provisioning subscription.
   If the client is already registered for users only,
   create a subscription with a different subscription name.
   Set :envvar:`provisioningApi.auth.username` to an unused name,
   for example ``scim-client-groups``, in :file:`scim-client-values.yaml`.

   To register the subscription for both users and user groups,
   apply both Helm updates in :ref:`scim-client-installation-helm`.
   The previous subscription remains registered and can accumulate unprocessed messages.

   After you have verified the new subscription for users and user groups,
   remove the previous subscription after the *SCIM Client* has processed its pending messages
   or the subscription is no longer needed.
   To delete a subscription,
   use :external+uv-nubus-customization:ref:`customization-api-provisioning-interactive-openapi-schema-delete-subscriptions`
   in :cite:t:`uv-nubus-customization`.
   The documentation also explains API access and administrative credentials.
   Deleting a subscription discards its remaining queued messages.

.. _scim-client-provisioning-multiple:

Multiple SCIM targets
---------------------

This section describes how you set up *SCIM Client* for multiple *SCIM targets*.
For each additional *SCIM target*,
prepare a separate client values file as described in :ref:`scim-client-configuration`.
Configure the target's URL and authentication credentials,
and use a separate PostgreSQL database for each client.
The clients can share the same LDAP connection and existing LDAP secret.

Use a different Helm release name for each client in the Nubus namespace.
The following example uses the releases ``scim-client-a`` and ``scim-client-b``.
It uses the chart's default resource names
and creates registration secrets from :envvar:`provisioningApi.auth.password`.
Leave ``nameOverride``, ``fullnameOverride``,
and :envvar:`provisioningApi.auth.existingSecret.name` unset for this example.

#. Define the subscription credentials in :file:`scim-client-a-values.yaml`
   and :file:`scim-client-b-values.yaml`,
   as shown in :numref:`scim-client-provisioning-multiple-a-listing`
   and :numref:`scim-client-provisioning-multiple-b-listing`.
   Subscription names must be unique within the Nubus deployment.

   Replace the following placeholders, including the angle brackets:

   - ``SUBSCRIPTION_PASSWORD_A`` with the subscription password for client A.
   - ``SUBSCRIPTION_PASSWORD_B`` with the subscription password for client B.

   These release names produce the registration secrets
   ``scim-client-a-provisioning`` and ``scim-client-b-provisioning``.

   .. code-block:: yaml
      :caption: Subscription settings in :file:`scim-client-a-values.yaml`
      :name: scim-client-provisioning-multiple-a-listing

      provisioningApi:
        auth:
          username: "scim-client-a"
          password: "<SUBSCRIPTION_PASSWORD_A>"

   .. code-block:: yaml
      :caption: Subscription settings in :file:`scim-client-b-values.yaml`
      :name: scim-client-provisioning-multiple-b-listing

      provisioningApi:
        auth:
          username: "scim-client-b"
          password: "<SUBSCRIPTION_PASSWORD_B>"

#. Add a separate consumer entry for each secret in :file:`nubus-values.yaml`,
   as shown in :numref:`scim-client-provisioning-multiple-registration-listing`.
   Keep all existing consumer entries.
   The entry names ``scimClientA`` and ``scimClientB`` must also be distinct.

   .. code-block:: yaml
      :caption: Register both clients in the Nubus values file
      :name: scim-client-provisioning-multiple-registration-listing

      nubusProvisioning:
        registerConsumers:
          createUsers:
            scimClientA:
              existingSecret:
                name: "scim-client-a-provisioning"
                keyMapping:
                  registration: "registration"
            scimClientB:
              existingSecret:
                name: "scim-client-b-provisioning"
                keyMapping:
                  registration: "registration"

#. Prepare the environment variables in :ref:`scim-client-installation-helm`.
   Then install both client releases with their respective values files,
   as shown in :numref:`scim-client-provisioning-multiple-install-listing`.

   .. code-block:: console
      :caption: Install the clients for both SCIM targets
      :name: scim-client-provisioning-multiple-install-listing

      $ helm upgrade \
          --install \
          scim-client-a \
          --namespace "$NUBUS_NAMESPACE" \
          oci://artifacts.software-univention.de/nubus/charts/scim-client \
          --version "$SCIM_CLIENT_HELM_VERSION" \
          --values scim-client-a-values.yaml

      $ helm upgrade \
          --install \
          scim-client-b \
          --namespace "$NUBUS_NAMESPACE" \
          oci://artifacts.software-univention.de/nubus/charts/scim-client \
          --version "$SCIM_CLIENT_HELM_VERSION" \
          --values scim-client-b-values.yaml

#. After you install both clients,
   apply the Nubus update in :numref:`scim-client-deployment-subscription-listing`
   once to register both subscriptions.
   Retain any additional Nubus values files as described in those instructions.
   To verify the deployment status of each client,
   follow :ref:`scim-client-installation-verify`
   and use the corresponding release name in place of ``scim-client``.
