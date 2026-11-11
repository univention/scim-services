.. SPDX-License-Identifier: AGPL-3.0-only
.. SPDX-FileCopyrightText: 2026 Univention GmbH

.. _scim-client-setup-and-operation:

*******************
Setup and operation
*******************

This chapter is for operators who set up and operate the *SCIM Client*.
It assumes that you are familiar with Kubernetes and Helm.
The following sections cover the prerequisites, configuration, installation,
and troubleshooting.

:ref:`scim-client-prerquesites`
   The *SCIM Client* requires access to Nubus and a *SCIM target*.
   Check the required services, credentials, and connections before installation.

:ref:`scim-client-configuration`
   The *SCIM Client* uses a Helm Chart values file for its settings.
   Prepare the connection details, authentication credentials,
   and optional settings for your environment.

:ref:`scim-client-provisioning`
   The *SCIM Client* receives changes from the Nubus *Provisioning Service*
   through a subscription.
   Configure a separate client and subscription for each *SCIM target*.

:ref:`scim-client-installation`
   The *SCIM Client* and Nubus use separate Helm releases.
   Install or update the client and verify its deployment status.

:ref:`scim-client-troubleshooting`
   Provisioning tasks can fail or remain pending.
   Check logs and task status, investigate errors, and retry failed tasks.

.. toctree::
   :caption: Contents

   prerequisites
   configuration
   provisioning
   installation
   troubleshooting
