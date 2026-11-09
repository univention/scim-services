.. SPDX-License-Identifier: AGPL-3.0-only

.. SPDX-FileCopyrightText: 2025-2026 Univention GmbH

.. _scim-client-intro:

************
Introduction
************

The *SCIM Client* provisions users and user groups from Nubus for Kubernetes to an external application using the System for Cross-domain Identity Management (SCIM) protocol.
The external application provides a SCIM server interface.
This manual refers to that application as the *SCIM target*.

This manual is for operators who connect applications to Nubus for Kubernetes and for software vendors who implement a SCIM interface in their applications.

If you operate the *SCIM Client*, start with the :ref:`scim-client-prerquesites`.
The installation and configuration procedures assume that you are familiar with Kubernetes and Helm.

If you develop a SCIM interface for an application,
start with :ref:`scim-client-target-integration-requirements`.
That chapter describes the requests the client sends and the responses it expects from your application.

For installation and operation of Nubus for Kubernetes itself, see the :external+uv-nubus-kubernetes-operation:ref:`Nubus for Kubernetes Operation Manual <doc-entry>`.
