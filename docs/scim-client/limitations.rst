.. SPDX-FileCopyrightText: 2025 Univention GmbH
..
.. SPDX-License-Identifier: AGPL-3.0-only

.. _conf-scim-client-limitations:

Limitations
===========

Consider the following limitations when integrating a SCIM target with the *SCIM Client*.

.. _conf-scim-client-limitations-data-sync:

Data synchronization
--------------------

When user group provisioning is enabled, the following limitations apply.

Group membership sync
   * The *SCIM Client* includes direct user members in the ``members`` attribute of a ``Group``.

   * It doesn't populate the ``groups`` attribute of a ``User``.

   * It doesn't include nested groups as members of a ``Group``.

.. _conf-scim-client-limitations-configuration:

Configuration
-------------

Attribute mapping
   You can configure the UDM source attributes for the following SCIM fields:

   * ``externalId`` for users and user groups, through :envvar:`scimClient.config.externalIdUserMapping` and :envvar:`scimClient.config.externalIdGroupMapping`.

   * ``userName`` for users, through ``scimClient.config.usernameMapping``.

   The mappings for other fields are fixed.
