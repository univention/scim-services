.. SPDX-FileCopyrightText: 2025 Univention GmbH
..
.. SPDX-License-Identifier: AGPL-3.0-only

.. _conf-scim-client-schemas:

Supported schemas
=================

The *SCIM Client* supports the following schemas for provisioning:

* :ref:`conf-scim-client-schemas-user`
* :ref:`conf-scim-client-schemas-group`

.. _conf-scim-client-schemas-user:

User schema
-----------

The client supports the core User schema as defined in :rfc:`7643`
and the following extensions:

* ``urn:ietf:params:scim:schemas:core:2.0:User``
* ``urn:ietf:params:scim:schemas:extension:enterprise:2.0:User``
* ``urn:ietf:params:scim:schemas:extension:Univention:1.0:User``
* ``urn:ietf:params:scim:schemas:extension:DapUser:2.0:User``

.. _conf-scim-client-schemas-group:

Group schema
------------

The client supports the core Group schema as defined in :rfc:`7643`
and the following extensions:

* ``urn:ietf:params:scim:schemas:core:2.0:Group``
* ``urn:ietf:params:scim:schemas:extension:Univention:1.0:Group``
