.. SPDX-FileCopyrightText: 2025 Univention GmbH
..
.. SPDX-License-Identifier: AGPL-3.0-only

.. _conf-scim-client-provisioning:

Provisioning subscription
=========================

The *SCIM Client* receives user and user group changes from the Nubus *Provisioning Service* through a subscription.
Configure a separate client and subscription for each SCIM target.

In the setup described in this manual, the *SCIM Client* Helm Chart creates a Secret with the registration data for its subscription.
The Nubus deployment uses this data to register the client with the *Provisioning Service*.

Add the configuration in :numref:`conf-scim-client-provisioning-listing` to the :file:`nubus-values.yaml` file for your existing Nubus deployment.
If ``nubusProvisioning.registerConsumers.createUsers`` already exists, add the ``scimClient`` entry to it and keep the existing entries.
The configuration references the ``registration`` entry in the ``scim-client-provisioning`` Secret.
This entry contains the subscription name, topics, prefill setting, and password.

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
               registration: "registration"

After preparing both values files, continue with :ref:`conf-scim-client-installation`.
