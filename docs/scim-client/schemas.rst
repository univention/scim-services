.. SPDX-FileCopyrightText: 2025 Univention GmbH
..
.. SPDX-License-Identifier: AGPL-3.0-only

.. _scim-client-schemas:

Supported schemas
=================

SCIM schemas define the attributes of users and user groups.
The *SCIM Client* detects the schemas supported by the SCIM target and uses the matching extensions.
The target doesn't need to support all the extensions listed below.
Advertising an additional extension doesn't provide a mapping for arbitrary application-specific attributes.
The client maps the attributes described in this chapter.

The *SCIM Client* supports the following schemas when provisioning data to a SCIM target:

* :ref:`scim-client-schemas-user`
* :ref:`scim-client-schemas-group`

.. _scim-client-schemas-user:

User schema
-----------

The following list includes the core ``User`` schema from :rfc:`7643` and the supported extensions:

* ``urn:ietf:params:scim:schemas:core:2.0:User``
* ``urn:ietf:params:scim:schemas:extension:enterprise:2.0:User``
* ``urn:ietf:params:scim:schemas:extension:Univention:1.0:User``
* ``urn:ietf:params:scim:schemas:extension:UniventionUser:2.0:User``

.. _scim-client-schemas-user-attributes:

User attributes
~~~~~~~~~~~~~~~

The core ``User`` schema requires ``userName``.
The *SCIM Client* also requires a nonempty ``externalId`` to identify the corresponding resource at the target.
The target assigns its own ``id``; see :ref:`scim-client-integration-identifiers`.

:numref:`scim-client-schemas-user-attributes-table` shows the available core mappings.
The other mapped attributes are optional from the client's perspective and depend on the available source data and the target's schema.
If your application requires additional attributes, make sure that Nubus provides the corresponding values and that the client has a mapping for them.
The client doesn't send a ``password`` attribute.
Configure user sign-in separately in the target application, for example through single sign-on or the application's invitation and password setup process.

.. _scim-client-schemas-user-attributes-table:

.. list-table:: Core user attribute mapping
   :header-rows: 1
   :widths: 2 3 4

   * - SCIM attribute
     - Nubus UDM property
     - Mapping
   * - ``externalId``
     - ``univentionObjectIdentifier`` by default
     - Required by the client; configurable through ``scimClient.config.externalIdUserMapping``.
   * - ``userName``
     - ``username`` by default
     - Required for a user; configurable through ``scimClient.config.usernameMapping``.
   * - ``active``
     - ``disabled``
     - The inverse Boolean value: a disabled user maps to ``active: false``.
   * - ``name.givenName``
     - ``firstname``
     - The user's first name.
   * - ``name.familyName``
     - ``lastname``
     - The user's last name.
   * - ``name.formatted``
     - ``firstname``, ``lastname``
     - First and last name, joined with a space when both are present.
   * - ``displayName``
     - ``displayName``
     - The source display name.
   * - ``title``
     - ``title``
     - The source title.
   * - ``userType``
     - ``employeeType``
     - The source employee type.
   * - ``preferredLanguage``
     - ``preferredLanguage``
     - The source language preference.
   * - ``emails``
     - ``mailPrimaryAddress``, ``mailAlternativeAddress``, ``e-mail``
     - Entries with types ``mailbox``, ``alias``, and ``other``, respectively.
       The client sets ``primary`` to ``false`` for each entry.
   * - ``phoneNumbers``
     - ``phone``, ``mobileTelephoneNumber``, ``homeTelephoneNumber``, ``pagerTelephoneNumber``
     - Entries with types ``work``, ``mobile``, ``home``, and ``pager``, respectively.
   * - ``addresses``
     - ``street``, ``city``, ``postcode``, ``state``, ``country``, ``homePostalAddress``
     - A work address from the individual properties and home addresses from ``homePostalAddress``.
   * - ``roles``
     - ``guardianRoles``, ``guardianInheritedRoles``
     - Entries with types ``guardian-direct`` and ``guardian-indirect``, respectively.
   * - ``photos``
     - ``jpegPhoto``
     - A photo entry with a ``data:image/jpeg;base64,...`` URI.
   * - ``x509Certificates``
     - ``userCertificate``, ``certificateSubjectCommonName``
     - A certificate entry with the certificate as ``value`` and its common name as ``display``.

.. _scim-client-schemas-user-extensions:

User extension attributes
~~~~~~~~~~~~~~~~~~~~~~~~~

The client maps the following extension attributes when the target advertises the corresponding extension:

``urn:ietf:params:scim:schemas:extension:enterprise:2.0:User``
   ``employeeNumber`` from the Nubus ``employeeNumber`` property.
   Other enterprise attributes, such as ``department`` or ``manager``, aren't mapped.

``urn:ietf:params:scim:schemas:extension:Univention:1.0:User``
   ``description`` from ``description`` and ``passwordRecoveryEmail`` from ``PasswordRecoveryEmail``.

``urn:ietf:params:scim:schemas:extension:UniventionUser:2.0:User``
   ``primaryOrgUnit`` and ``secondaryOrgUnits`` from the corresponding Nubus properties.

.. _scim-client-schemas-group:

Group schema
------------

The following list includes the core ``Group`` schema from :rfc:`7643` and the supported extension:

* ``urn:ietf:params:scim:schemas:core:2.0:Group``
* ``urn:ietf:params:scim:schemas:extension:Univention:1.0:Group``

The ``scimClient.config.groupSync`` setting controls whether the client provisions user groups; see :ref:`scim-client-configuration-optional`.

.. _scim-client-schemas-group-attributes:

Group attributes
~~~~~~~~~~~~~~~~

The core ``Group`` schema requires ``displayName``.
:numref:`scim-client-schemas-group-attributes-table` shows the available core mappings.

.. list-table:: Core group attribute mapping
   :name: scim-client-schemas-group-attributes-table
   :header-rows: 1
   :widths: 2 3 4

   * - SCIM attribute
     - Nubus UDM property
     - Mapping
   * - ``externalId``
     - ``univentionObjectIdentifier`` by default
     - Required by the client; configurable through ``scimClient.config.externalIdGroupMapping``.
   * - ``displayName``
     - ``name``
     - Required for a group; the source group name.
   * - ``members``
     - ``users``
     - Direct user memberships, resolved to the corresponding users at the SCIM target.

For direct user memberships, the client maps the target-assigned user ID to ``members.value``.
It also maps ``type: User`` and the target user's ``displayName`` to ``display`` when the target's schema supports them.
Members that the client can't find at the SCIM target are omitted.
For the group membership restrictions, see :ref:`scim-client-limitations-data-sync`.

.. _scim-client-schemas-group-extensions:

Group extension attributes
~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``urn:ietf:params:scim:schemas:extension:Univention:1.0:Group`` extension adds ``description`` from the Nubus group ``description`` property.
It also maps ``guardianMemberRoles`` to ``memberRoles`` entries with ``type: guardian``.
