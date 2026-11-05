.. SPDX-License-Identifier: AGPL-3.0-only

.. SPDX-FileCopyrightText: 2025-2026 Univention GmbH

.. _introduction:

.. _conf-scim-client:

************
Introduction
************

Use the *SCIM Client* for a setup to provision user and user group information
from Nubus for Kubernetes to an external target.

.. important::

   The *SCIM Client* is experimental and intended for preliminary testing only.
   It isn't yet recommended for production use.

This page describes how to deploy and configure the *SCIM Client* for Nubus for Kubernetes.
The *SCIM Client* acts as a connector to provision users and user groups to a SCIM-compliant downstream application
that's external to Nubus for Kubernetes.

This page is for operators
that want to integrate a downstream application with Nubus for Kubernetes through SCIM.
