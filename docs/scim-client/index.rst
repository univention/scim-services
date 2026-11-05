.. SPDX-License-Identifier: AGPL-3.0-only

.. SPDX-FileCopyrightText: 2025-2026 Univention GmbH

.. _introduction:

.. _conf-scim-client:

************
Introduction
************

The *SCIM Client* provisions users and user groups from Nubus for Kubernetes to an external application using the System for Cross-domain Identity Management (SCIM) protocol.
This manual refers to the external application as the *SCIM target*.

This manual is for operators who want to connect an application with a SCIM interface to Nubus for Kubernetes.
It describes how to install and configure the *SCIM Client*, set up provisioning, and troubleshoot problems.
You need to be familiar with Kubernetes and Helm.

Before you start, check the :ref:`conf-scim-client-installation-prerequisites`.
For installation and operation of Nubus for Kubernetes itself, see the :external+uv-nubus-kubernetes-operation:ref:`Nubus for Kubernetes Operation Manual <doc-entry>`.
