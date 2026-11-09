.. SPDX-FileCopyrightText: 2025 Univention GmbH
..
.. SPDX-License-Identifier: AGPL-3.0-only

.. _scim-client-limitations:

Limitations
===========

The following limitations apply to the current *SCIM Client* implementation when integrating a SCIM target.

.. _scim-client-limitations-data-sync:

Data synchronization
--------------------

When user group provisioning is enabled, the client writes memberships through the ``members`` attribute of a ``Group``.
In accordance with :rfc:`7643`, it doesn't write the read-only ``groups`` attribute of a ``User``.

The following restrictions apply to the client's handling of group members:

Group membership sync
   * The *SCIM Client* includes direct user members only.
     SCIM supports nested groups, but the client doesn't include them as members of a ``Group``.

   * Member lookup uses the user's Nubus ``univentionObjectIdentifier`` as the SCIM ``externalId``.
     If a custom user ``externalId`` mapping produces a different value, the client can't resolve that member.

.. _scim-client-limitations-configuration:

Configuration
-------------

Attribute mapping
   You can only configure the UDM source attributes for the following SCIM fields:

   * ``externalId`` for users and user groups, through :envvar:`scimClient.config.externalIdUserMapping` and :envvar:`scimClient.config.externalIdGroupMapping`.

   * ``userName`` for users, through ``scimClient.config.usernameMapping``.

   Changing the UDM source property for other SCIM attributes requires a change to the mapping code.
