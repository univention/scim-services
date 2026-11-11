.. SPDX-FileCopyrightText: 2025 Univention GmbH
..
.. SPDX-License-Identifier: AGPL-3.0-only

.. _scim-client-limitations:

Limitations
===========

The following limitations apply to the *SCIM Client* implementation
when integrating a *SCIM target*.

.. _scim-client-limitations-data-sync:

Data synchronization
--------------------

When you enable user group provisioning through :envvar:`scimClient.config.groupSync`,
the *SCIM Client* writes memberships through the ``members`` attribute of a ``Group``.
In accordance with :rfc:`7643`,
it doesn't write the read-only ``groups`` attribute of a ``User``.

The following restrictions apply to the client's handling of group members:

Group membership synchronization
   * The *SCIM Client* includes direct user members only.
     SCIM supports nested groups,
     but the client doesn't include them as members of a ``Group``.

   * The client resolves member distinguished names (DNs)
     from provisioning events against the current LDAP data.
     If a user has been renamed or moved,
     an older event can refer to a DN that no longer exists.

   * Member lookup uses the user's Nubus ``univentionObjectIdentifier``
     as the SCIM :ref:`scim-client-schemas-user-attributes-externalid` attribute.
     If a custom user ``externalId`` mapping produces a different value,
     the client can't resolve that member.

   The client omits members that it can't resolve
   from the group sent to the *SCIM target*.
   For group membership synchronization,
   keep :envvar:`scimClient.config.externalIdUserMapping`
   at its default value ``univentionObjectIdentifier``.

.. _scim-client-limitations-configuration:

Configuration
-------------

Attribute mapping
   You can configure the Univention Directory Manager (UDM) source attributes
   for only the following SCIM fields:

   * ``externalId`` for users and user groups,
     through :envvar:`scimClient.config.externalIdUserMapping` and :envvar:`scimClient.config.externalIdGroupMapping`, respectively.

   * ``userName`` for users, through :envvar:`scimClient.config.usernameMapping`.

   Changing the UDM source property for other SCIM attributes requires a change to the mapping code.
