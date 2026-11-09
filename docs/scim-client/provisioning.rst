.. SPDX-FileCopyrightText: 2025 Univention GmbH
..
.. SPDX-License-Identifier: AGPL-3.0-only

.. _scim-client-provisioning:

Provisioning subscription
=========================

The *SCIM Client* receives user and user group changes from the Nubus *Provisioning Service* through a subscription.
Configure a separate client and subscription for each SCIM target.

In the setup described in this manual, the *SCIM Client* Helm Chart creates a Secret with the registration data for its subscription.
The Nubus deployment uses this data to register the client with the *Provisioning Service*.

Add the configuration in :numref:`scim-client-provisioning-listing` to the :file:`nubus-values.yaml` file for your existing Nubus deployment.
If ``nubusProvisioning.registerConsumers.createUsers`` already exists, add the ``scimClient`` entry to it and keep the existing entries.
The configuration references the ``registration`` entry in the ``scim-client-provisioning`` Secret.
This entry contains the subscription name, topics, prefill setting, and password.

.. code-block:: yaml
   :caption: Add subscription for *SCIM Client* to Nubus for Kubernetes Helm Chart
   :name: scim-client-provisioning-listing

   nubusProvisioning:
     registerConsumers:
       createUsers:
         scimClient:
           existingSecret:
             name: scim-client-provisioning
             keyMapping:
               registration: "registration"

.. note::

   If you enable ``scimClient.config.groupSync`` after registering the client for users only, use a new subscription name with Nubus for Kubernetes 1.24.0.
   This version doesn't support changing the topics of an existing subscription.
   Set ``provisioningApi.auth.username`` to an unused name, for example ``scim-client-groups``, in :file:`scim-client-values.yaml`.
   Apply both Helm updates in :ref:`conf-scim-client-installation-helm` to register the new subscription for both users and user groups.
   The previous subscription remains registered and can accumulate unprocessed messages.

   After verifying the new subscription, remove the old one once its pending messages have been processed or are no longer needed.
   Use ``DELETE /v1/subscriptions/{name}`` as described in the `Provisioning API documentation <https://docs.software-univention.de/nubus-customization/latest/en/api/provisioning.html#openapi-schema>`_, which also explains API access and administrative credentials.
   Deleting a subscription discards its remaining queued messages.

After preparing both values files, continue with :ref:`conf-scim-client-installation`.
