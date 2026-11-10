.. SPDX-FileCopyrightText: 2025 Univention GmbH
..
.. SPDX-License-Identifier: AGPL-3.0-only

.. _scim-client-provisioning:

Provisioning subscription
=========================

The *SCIM Client* receives user and user group changes
from the Nubus *Provisioning Service* through a subscription.
Configure a separate client and subscription for each *SCIM target*.

In the setup described in this manual,
the *SCIM Client* Helm Chart creates a secret with the registration data for its subscription.
The Nubus deployment uses this data to register the client with the *Provisioning Service*.

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
