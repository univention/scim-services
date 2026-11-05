.. SPDX-FileCopyrightText: 2025 Univention GmbH
..
.. SPDX-License-Identifier: AGPL-3.0-only

.. _conf-scim-client-configuration:

Configuration
=============

This section describes the configuration options for the *SCIM Client*.

To configure the *SCIM Client*,
you need to create a :file:`scim-client-values.yaml` values file for the *SCIM Client* Helm Chart.
The Helm Chart comes with default values.
For a list of all possible values,
see the ``values.yaml`` file in the Helm Chart of the *SCIM Client*.
This section distinguishes between mandatory and optional values.

.. _conf-scim-client-configuration-mandatory:

Mandatory values
----------------

You must set the values in this section
in your :file:`scim-client-values.yaml` values file.
Without these values, the *SCIM Client* doesn't work as expected.

The *SCIM Client* always needs the following values:

* :envvar:`scimServer.connection.url`: The URL of the SCIM target.
* :envvar:`provisioningApi.auth.username`: The username for the *Provisioning API*.
* :envvar:`provisioningApi.auth.password`: The password for the *Provisioning API*.
* :envvar:`ldap.auth.bindDn`: The bind DN for the *LDAP Server*.
* :envvar:`ldap.auth.existingSecret.name`: The name of the existing secret for the *LDAP Server*.
* :envvar:`scimClient.config.dbConnectionString`: The connection URL for the PostgreSQL database.

In addition,
you must configure authentication for the SCIM target.
The authentication method determines the required authentication values.
For more information,
see :ref:`conf-scim-client-configuration-auth`.

:numref:`conf-scim-client-configuration-mandatory-listing`
shows a minimal configuration example with OIDC authentication.

.. code-block:: yaml
   :caption: Minimal example for *SCIM Client* configuration
   :name: conf-scim-client-configuration-mandatory-listing

   scimClient:
     config:
       dbConnectionString: "postgresql+psycopg2://<DATABASE_USERNAME>:<PASSWORD>@<HOSTNAME>/<DATABASE_NAME>"

   scimServer:
     connection:
       url: "https://scim.example.com/scim/v2/"
     auth:
       method: "oidc"
       password: "your-client-secret"
       oidc:
         oidcTokenUrl: "https://auth.example.com/realms/nubus/protocol/openid-connect/token"
         clientId: "scim-client"

   provisioningApi:
     auth:
       username: "admin"
       password: "your-provisioning-api-password"

   ldap:
     auth:
       bindDn: "cn=admin,dc=swp-ldap,dc=internal"
       existingSecret:
         name: nubus-ldap-server-admin

.. _conf-scim-client-configuration-database:

Database
--------

The PostgreSQL database isn't included in the Helm Chart.
You are responsible for operating the database, including backups and upgrades.
The *SCIM Client* creates its tables on startup.

.. envvar:: scimClient.config.dbConnectionString

   The SQLAlchemy connection URL for the PostgreSQL database.
   You must set this value in your :file:`scim-client-values.yaml` file,
   as shown in :numref:`conf-scim-client-configuration-mandatory-listing`.
   The connection string uses the following pattern::

      postgresql+psycopg2://<DATABASE_USERNAME>:<PASSWORD>@<HOSTNAME>/<DATABASE_NAME>

   Replace ``<DATABASE_USERNAME>``,
   ``<PASSWORD>``,
   ``<HOSTNAME>``,
   and ``<DATABASE_NAME>`` with the values for your database connection.

   .. warning::

      Without the connection URL, a Helm installation or upgrade fails.
      The Helm Chart passes the value to the client through a Secret as ``PROVISIONING_DB``.

.. _conf-scim-client-configuration-auth:

Authentication for the SCIM target
-----------------------------------

The *SCIM Client* supports several authentication methods
for the SCIM target.
Set :envvar:`scimServer.auth.method`
to one of the values in :numref:`conf-scim-client-auth-methods-table`.

For all authentication methods except ``none``,
the *SCIM Client* needs a secret value for authentication.
The required value :envvar:`scimServer.auth.password`
can come either directly from the values file
or from an existing Kubernetes Secret configured with
:envvar:`scimServer.auth.existingSecret.name`.

The value ``none`` sends no ``Authorization`` header.
Use this value only for testing, never in production.

.. list-table:: Authentication methods for the SCIM target
   :name: conf-scim-client-auth-methods-table
   :header-rows: 1
   :widths: 1 6 5

   * - Value
     - Use case
     - Required values
   * - ``oidc``
     - Use *OpenID Connect* (OIDC) authentication.
     - | :envvar:`scimServer.auth.oidc.oidcTokenUrl`
       | :envvar:`scimServer.auth.oidc.clientId`
       | :envvar:`scimServer.auth.password`
   * - ``basic``
     - Use HTTP Basic authentication
       for SCIM targets that don't support OIDC.
     - | :envvar:`scimServer.auth.basic.username`
       | :envvar:`scimServer.auth.password`
   * - ``bearer``
     - Use static Bearer token authentication
       for SCIM targets that don't support OIDC.
     - :envvar:`scimServer.auth.password`
   * - ``none``
     - Don't send an ``Authorization`` header.
     - No authentication values required.

.. _conf-scim-client-configuration-optional:

Optional values
---------------

You can optionally override the following default values in your :file:`scim-client-values.yaml` values file.
:numref:`conf-scim-client-configuration-optional-listing` shows an example with all optional values.

:envvar:`scimClient.config.logLevel`
  The log level for the *SCIM Client*.
  The default value is ``INFO``.

:envvar:`scimClient.config.prefill`
  A boolean value to control
  if Nubus for Kubernetes shall provide existing user and user group data
  to the SCIM target through the provisioning subscription.
  The default value is ``true``.

:envvar:`scimClient.config.groupSync`
  A boolean value to control
  if Nubus for Kubernetes shall synchronize user groups.
  The default value is ``true``.

:envvar:`scimClient.config.externalIdUserMapping`
  The UDM attribute that UDM maps to the ``externalId`` field of *Users* in SCIM.
  The default value is ``univentionObjectIdentifier``.

:envvar:`scimClient.config.externalIdGroupMapping`
   The UDM attribute that UDM maps to the ``externalId`` field of *Groups* in SCIM.
   The default value is ``univentionObjectIdentifier``.

:envvar:`scimServer.auth.oidc.scopes`
   Only applies when :envvar:`scimServer.auth.method` is ``oidc``.
   A list of additional scopes to request when obtaining an OIDC access token for SCIM server authentication.
   The *SCIM Client* always automatically includes the ``openid`` scope.
   Use this option if the downstream SCIM server requires specific scopes in the access token.
   The default value is ``null``,
   which means that the *SCIM Client* doesn't use any additional scopes.

.. code-block:: yaml
   :caption: Example for optional *SCIM Client* configuration
   :name: conf-scim-client-configuration-optional-listing

   scimClient:
     config:
       logLevel: "DEBUG"
       prefill: false
       groupSync: false
       externalIdUserMapping: "customUserId"
       externalIdGroupMapping: "customGroupId"

   scimServer:
     auth:
       oidc:
         scopes:
           - "additionalScope1"
           - "additionalScope2"

.. note::

   The default value for the mapping is ``univentionObjectIdentifier`` for both users and user groups.
   If the SCIM target uses different attributes for user and user group IDs,
   you need to adapt the values for
   :envvar:`scimClient.config.externalIdUserMapping`
   and :envvar:`scimClient.config.externalIdGroupMapping`.
