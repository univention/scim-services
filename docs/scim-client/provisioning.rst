.. SPDX-FileCopyrightText: 2025 Univention GmbH
..
.. SPDX-License-Identifier: AGPL-3.0-only

.. _conf-scim-client-provisioning:

Provisioning subscription
=========================

The *SCIM Client* is a consumer of the *Provisioning Service* in Nubus for Kubernetes.
It requires a provisioning subscription to receive events about users and user groups.
For each SCIM target, you need to configure a *SCIM Client* consumer
by configuring a provisioning subscription for it.

To configure a provisioning subscription,
you need to register the consumer in the :file:`nubus-values.yaml` values file of your Nubus for Kubernetes installation,
not the Helm Chart for the *SCIM Client*.
The separation ensures
that the subscription is idempotent
and that you can manage it as part of your Nubus for Kubernetes installation.

To add a subscription for the *SCIM Client*,
add the configuration in
:numref:`conf-scim-client-provisioning-listing`
to your ``nubus-values.yaml`` values file.

.. code-block:: yaml
   :caption: Add subscription for *SCIM Client* to Nubus for Kubernetes Helm Chart
   :name: conf-scim-client-provisioning-listing

   nubusProvisioning:
     registerConsumers:
       createUsers:
         scimClient:
           existingSecret:
             name: scim-client-provisioning
             keyMapping:
               password: "registration"
