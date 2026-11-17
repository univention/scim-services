.. SPDX-FileCopyrightText: 2025 Univention GmbH
..
.. SPDX-License-Identifier: AGPL-3.0-only

.. _scim-client-schemas:

Supported schemas
=================

SCIM schemas define the attributes of users and user groups.
The *SCIM Client* detects the schemas supported by the *SCIM target*
and uses the matching extensions.
The target doesn't need to support all the extensions listed later.
Advertising an additional extension doesn't provide a mapping for arbitrary application-specific attributes.
The client maps the attributes described on this page.

The *SCIM Client* supports the following schemas
when provisioning data to an *SCIM target*:

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

The core ``User`` schema requires :ref:`scim-client-schemas-user-attributes-username`.
The *SCIM Client* also requires a nonempty :ref:`scim-client-schemas-user-attributes-externalid`
to identify the corresponding resource at the target.
The target assigns its own ``id``.
For information,
see :ref:`scim-client-target-integration-requirements-identifiers`.

The following list shows the available core mappings.
All other mapped attributes are optional from the client's perspective
and depend on the available source data and the target's schema.
If your application requires additional attributes,
make sure that Nubus provides the corresponding values
and that the client has a mapping for them.
The client doesn't send a ``password`` attribute.

Configure user sign-in separately in the target application,
for example through single sign-on or the application's invitation and password setup process.

.. _scim-client-schemas-user-attributes-externalid:

``externalId``
   :Nubus UDM property: ``univentionObjectIdentifier`` by default
   :Mapping: Required by the client.

      Configurable through :envvar:`scimClient.config.externalIdUserMapping`.

.. _scim-client-schemas-user-attributes-username:

``userName``
   :Nubus UDM property: ``username`` by default
   :Mapping: Required for a user.

      Configurable through :envvar:`scimClient.config.usernameMapping`.

.. _scim-client-schemas-user-attributes-active:

``active``
   :Nubus UDM property:  ``disabled``
   :Mapping: The inverse Boolean value.

      A deactivated user maps to ``active: false``.

.. _scim-client-schemas-user-attributes-name-givenname:

``name.givenName``
   :Nubus UDM property: ``firstname``
   :Mapping: The user's first name.

.. _scim-client-schemas-user-attributes-name-familyname:

``name.familyName``
   :Nubus UDM property: ``lastname``
   :Mapping: The user's last name.

.. _scim-client-schemas-user-attributes-name.formatted:

``name.formatted``
   :Nubus UDM properties: ``firstname``, ``lastname``
   :Mapping: First and last name, joined with a space when both are present.

.. _scim-client-schemas-user-attributes-displayname:

``displayName``
   :Nubus UDM property: ``displayName``
   :Mapping: The source display name.

.. _scim-client-schemas-user-attributes-title:

``title``
   :Nubus UDM property: ``title``
   :Mapping: The source title.

.. _scim-client-schemas-user-attributes-usertype:

``userType``
   :Nubus UDM property: ``employeeType``
   :Mapping: The source employee type.

.. _scim-client-schemas-user-attributes-preferredlanguage:

``preferredLanguage``
   :Nubus UDM property: ``preferredLanguage``
   :Mapping: The source language preference.

.. _scim-client-schemas-user-attributes-emails:

``emails``
   :Nubus UDM properties: ``mailPrimaryAddress``, ``mailAlternativeAddress``, ``e-mail``
   :Mappings: Entries with types ``mailbox``, ``alias``, and ``other``, respectively.

      The client sets ``primary`` to ``true`` for ``mailPrimaryAddress``.
      It sets ``primary`` to ``false`` for the other entries.

.. _scim-client-schemas-user-attributes-phonenumbers:

``phoneNumbers``
   :Nubus UDM properties: ``phone``, ``mobileTelephoneNumber``, ``homeTelephoneNumber``, ``pagerTelephoneNumber``
   :Mappings: Entries with types ``work``, ``mobile``, ``home``, and ``pager``, respectively.

.. _scim-client-schemas-user-attributes-addresses:

``addresses``
   :Nubus UDM properties: ``street``, ``city``, ``postcode``, ``state``, ``country``, ``homePostalAddress``
   :Mapping: A work address from the individual properties
      and home addresses from ``homePostalAddress``.

.. _scim-client-schemas-user-attributes-roles:

``roles``
   :Nubus UDM properties: ``guardianRoles``, ``guardianInheritedRoles``
   :Mapping: Entries with types ``guardian-direct`` and ``guardian-indirect``, respectively.

.. _scim-client-schemas-user-attributes-photos:

``photos``
   :Nubus UDM property: ``jpegPhoto``
   :Mapping: A photo entry with a ``data:image/jpeg;base64,...`` URI.

.. _scim-client-schemas-user-attributes-x509certificates:

``x509Certificates``
   :Nubus UDM properties: ``userCertificate``, ``certificateSubjectCommonName``
   :Mapping: A certificate entry with the certificate as ``value``
      and its common name as ``display``.

.. _scim-client-schemas-user-extensions:

User extension attributes
~~~~~~~~~~~~~~~~~~~~~~~~~

The client maps the following extension attributes
when the target advertises the corresponding extension:

``urn:ietf:params:scim:schemas:extension:enterprise:2.0:User``
   Other enterprise attributes, such as ``department`` or ``manager``, aren't mapped.

   ``employeeNumber``
      :Nubus UDM property: ``employeeNumber``

``urn:ietf:params:scim:schemas:extension:Univention:1.0:User``
   ``description``
      :Nubus UDM property: ``description``

   ``passwordRecoveryEmail``
      :Nubus UDM property: ``PasswordRecoveryEmail``

``urn:ietf:params:scim:schemas:extension:UniventionUser:2.0:User``
   ``primaryOrgUnit``
      :Nubus UDM property: ``primaryOrgUnit``

   ``secondaryOrgUnits``
      :Nubus UDM property: ``secondaryOrgUnits``

.. _scim-client-schemas-group:

Group schema
------------

The following list includes the core ``Group`` schema from :rfc:`7643`
and the supported extension:

* ``urn:ietf:params:scim:schemas:core:2.0:Group``
* ``urn:ietf:params:scim:schemas:extension:Univention:1.0:Group``

The :envvar:`scimClient.config.groupSync` setting controls
whether the client provisions user groups.
For more information,
see :ref:`scim-client-configuration-optional`.

.. _scim-client-schemas-group-attributes:

Group attributes
~~~~~~~~~~~~~~~~

The core ``Group`` schema requires :ref:`scim-client-schemas-group-attributes-displayname`.
The following list shows the available core mappings.

.. _scim-client-schemas-group-attributes-externalid:

``externalId``
   :Nubus UDM property: ``univentionObjectIdentifier`` by default
   :Mapping: Required by the client.
      Configurable through :envvar:`scimClient.config.externalIdGroupMapping`.

.. _scim-client-schemas-group-attributes-displayname:

``displayName``
   :Nubus UDM property: ``name``
   :Mapping: Required for a group.
      The source group name.

.. _scim-client-schemas-group-attributes-members:

``members``
   :Nubus UDM property: ``users``
   :Mapping: Direct user memberships,
      resolved to the corresponding users at the *SCIM target*.

For direct user memberships,
the client maps the target-assigned user ID to ``members.value``.
It also maps ``type: User``
and the target user's ``displayName`` to ``display``
when the target's schema supports these attributes.
The client omits members that it can't find at the *SCIM target*.
For the group membership restrictions, see :ref:`scim-client-limitations-data-sync`.

.. _scim-client-schemas-group-extensions:

Group extension attributes
~~~~~~~~~~~~~~~~~~~~~~~~~~

The client maps the following extension attributes
when the target advertises the corresponding extension:

``urn:ietf:params:scim:schemas:extension:Univention:1.0:Group``
   ``description``
      :Nubus UDM property: ``description``

   ``guardianMemberRoles``
      :Nubus UDM property: ``memberRoles``
      :Mapping: Entries with ``type: guardian``.
