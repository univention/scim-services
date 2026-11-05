.. SPDX-FileCopyrightText: 2025 Univention GmbH
..
.. SPDX-License-Identifier: AGPL-3.0-only

.. _conf-scim-client-schemas:

Supported schemas
=================

SCIM schemas define the attributes of users and user groups.
The *SCIM Client* detects the schemas supported by the SCIM target and uses the matching extensions.
The target doesn't need to support all the extensions listed below.

The *SCIM Client* supports the following schemas when provisioning data to a SCIM target:

* :ref:`conf-scim-client-schemas-user`
* :ref:`conf-scim-client-schemas-group`

.. _conf-scim-client-schemas-user:

User schema
-----------

The following list includes the core ``User`` schema from :rfc:`7643` and the supported extensions:

* ``urn:ietf:params:scim:schemas:core:2.0:User``
* ``urn:ietf:params:scim:schemas:extension:enterprise:2.0:User``
* ``urn:ietf:params:scim:schemas:extension:Univention:1.0:User``
* ``urn:ietf:params:scim:schemas:extension:UniventionUser:2.0:User``

.. _conf-scim-client-schemas-group:

Group schema
------------

The following list includes the core ``Group`` schema from :rfc:`7643` and the supported extension:

* ``urn:ietf:params:scim:schemas:core:2.0:Group``
* ``urn:ietf:params:scim:schemas:extension:Univention:1.0:Group``

The ``scimClient.config.groupSync`` setting controls whether the client provisions user groups; see :ref:`conf-scim-client-configuration-optional`.
