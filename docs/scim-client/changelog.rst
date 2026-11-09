.. SPDX-FileCopyrightText: 2026 Univention GmbH
..
.. SPDX-License-Identifier: AGPL-3.0-only

.. _scim-client-changelog:

Changelog
=========

This changelog summarizes notable changes to the *SCIM Client* from version 0.49.0 onward.
For the complete release notes for SCIM Services, see `SCIM Services releases <https://git.knut.univention.de/univention/dev/projects/scim/scim-services/-/releases>`_.

.. _scim-client-changelog-v0.55.5:

v0.55.5
-------

Released: 2026-11-05

Fixed
~~~~~

* Improve compatibility with Wire's SCIM schema discovery and response format.
* Detect SCIM error responses when processing requests so that failed provisioning tasks enter error handling.

.. _scim-client-changelog-v0.55.0:

v0.55.0
-------

Released: 2026-10-05

Added
~~~~~

* Store provisioning tasks, their processing state, and errors in a PostgreSQL database.
* Add task management commands to inspect failed tasks and retry them after resolving the cause.
  See :ref:`scim-client-troubleshooting-cli`.

Fixed
~~~~~

* Retry network failures during SCIM discovery and reconnect after idle LDAP disconnects.
* Include error details from the SCIM target when recording failed tasks.

Upgrade
~~~~~~~

Before upgrading from an earlier version, prepare a separate PostgreSQL database and set ``scimClient.config.dbConnectionString`` in :file:`scim-client-values.yaml`.
The database is required and isn't included in the Helm Chart.
See :ref:`scim-client-configuration-database` for the connection settings.

.. _scim-client-changelog-v0.54.0:

v0.54.0
-------

Released: 2026-09-09

Added
~~~~~

* Make group provisioning optional through ``scimClient.config.groupSync``.
  Group provisioning is disabled by default.
  See :ref:`scim-client-configuration-selection` and :ref:`scim-client-provisioning`.
* Check the SCIM target's advertised capabilities and authentication methods, and log warnings about missing support.

.. _scim-client-changelog-v0.53.0:

v0.53.0
-------

Released: 2026-09-02

Added
~~~~~

* Map the UDM ``jpegPhoto`` property to the SCIM ``photos`` attribute.
* Send only attributes supported by the SCIM target's discovered schemas.

Fixed
~~~~~

* Use the configured ``externalId`` mapping when deleting an object from the SCIM target.

.. _scim-client-changelog-v0.52.0:

v0.52.0
-------

Released: 2026-08-24

Added
~~~~~

* Add ``SCIM_GROUP_FILTER_ATTRIBUTE`` to select which user groups to provision based on a UDM property.
  See :ref:`scim-client-configuration-selection`.

.. _scim-client-changelog-v0.51.0:

v0.51.0
-------

Released: 2026-08-17

Added
~~~~~

* Allow the UDM property used for the SCIM ``userName`` attribute to be configured.

.. _scim-client-changelog-v0.49.0:

v0.49.0
-------

Released: 2026-08-06

Added
~~~~~

* Support HTTP Basic authentication and static Bearer tokens for SCIM targets in addition to OIDC authentication.
  See :ref:`scim-client-configuration-auth`.
