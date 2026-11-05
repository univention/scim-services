.. SPDX-FileCopyrightText: 2025 Univention GmbH
..
.. SPDX-License-Identifier: AGPL-3.0-only

.. _conf-scim-client-limitations:

Limitations
===========

.. important::

   The *SCIM Client* is experimental and intended for preliminary testing only.
   It isn't yet recommended for production use.

This section outlines the current limitations and considerations when using the *SCIM Client*.

.. _conf-scim-client-limitations-data-sync:

Data synchronization
--------------------

Limitations on how the *SCIM Client* synchronizes user and user group data to the SCIM target.

Group membership sync
   * The *SCIM Client* synchronizes the list of direct members of a ``Group``,
     but not the list of groups that include a ``User``.

   * The *SCIM Client* lists only ``User`` objects as members of ``Group`` objects.
     It doesn't synchronize other member ``Group`` objects, such as nested groups.

.. _conf-scim-client-limitations-configuration:

Configuration
-------------

Limitations on the configuration of the *SCIM Client*.

Attribute mapping
   * Limited configuration for attribute mapping between UDM and SCIM schemas.

   * You can only customize the ``externalId`` field mapping
     through the ``externalIdUserMapping`` and ``externalIdGroupMapping`` configuration options.

   * Fixed attribute mapping for other SCIM fields, not customizable through configuration.
