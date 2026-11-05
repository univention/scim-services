.. SPDX-FileCopyrightText: 2025 Univention GmbH
..
.. SPDX-License-Identifier: AGPL-3.0-only

.. _conf-scim-client-configuration:

Prepare the client configuration
================================

Helm reads the client settings from a values file when it installs or updates the *SCIM Client*.
Create a :file:`scim-client-values.yaml` file before you run the installation commands.
Use this file to set the connection details and authentication credentials for your environment.
The following sections describe the required settings and selected optional values.
The chart's :file:`values.yaml` file lists all available settings and their defaults.

.. _conf-scim-client-configuration-mandatory:

Mandatory values
----------------

The *SCIM Client* needs connection details for the SCIM target, the Nubus *Provisioning API*, the *LDAP Server*, and its PostgreSQL database.
Set the following values in your :file:`scim-client-values.yaml` file:

* :envvar:`scimServer.connection.url`: The URL of the SCIM target.
* :envvar:`provisioningApi.connection.url`: The URL of the *Provisioning API*.
* :envvar:`ldap.connection.host`: The hostname of the *LDAP Server*.
* :envvar:`ldap.auth.bindDn`: The bind DN for the *LDAP Server*.
* :envvar:`scimClient.config.dbConnectionString`: The connection URL for the PostgreSQL database.

For authentication with the *Provisioning API*, set :envvar:`provisioningApi.auth.username` to the name of the provisioning subscription.
In this procedure, the chart creates the Secret for the provisioning subscription from :envvar:`provisioningApi.auth.password`.
For LDAP authentication, provide either :envvar:`ldap.auth.password` or :envvar:`ldap.auth.existingSecret.name`.
The example below uses an existing LDAP Secret from the Nubus deployment.

You also need to configure authentication for the SCIM target.
The authentication method determines the required authentication values.
For details, see :ref:`conf-scim-client-configuration-auth`.

:numref:`conf-scim-client-configuration-mandatory-listing` shows a configuration example with OIDC authentication.
Replace the URLs, credentials, database connection details, and LDAP settings with the values for your environment.

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
     connection:
       url: "<PROVISIONING_API_URL>"
     auth:
       username: "scim-client"
       password: "your-provisioning-api-password"

   ldap:
     connection:
       host: "<LDAP_HOSTNAME>"
     auth:
       bindDn: "cn=admin,dc=swp-ldap,dc=internal"
       existingSecret:
         name: nubus-ldap-server-admin

.. _conf-scim-client-configuration-database:

Database
--------

The *SCIM Client* uses PostgreSQL to store provisioning tasks, their processing state, and information about failed tasks.
This data supports retries and helps you investigate provisioning errors.
For details on inspecting tasks and errors, see :ref:`conf-scim-client-troubleshooting-cli`.

The PostgreSQL database isn't included in the Helm Chart.
You are responsible for operating the database, including backups and upgrades.
The *SCIM Client* creates its tables on startup.

Set :envvar:`scimClient.config.dbConnectionString` to the SQLAlchemy connection URL for the PostgreSQL database.
Add this value to your :file:`scim-client-values.yaml` file, as shown in :numref:`conf-scim-client-configuration-mandatory-listing`.
The connection string uses the following pattern::

   postgresql+psycopg2://<DATABASE_USERNAME>:<PASSWORD>@<HOSTNAME>/<DATABASE_NAME>

Replace ``<DATABASE_USERNAME>``, ``<PASSWORD>``, ``<HOSTNAME>``, and ``<DATABASE_NAME>`` with the values for your database connection.

.. warning::

   Without the connection URL, a Helm installation or upgrade fails.
   The Helm Chart passes the value to the client through a Secret as ``PROVISIONING_DB``.

.. _conf-scim-client-configuration-auth:

Authentication for the SCIM target
-----------------------------------

Set :envvar:`scimServer.auth.method` to one of the values in :numref:`conf-scim-client-auth-methods-table`.

For all authentication methods except ``none``, the *SCIM Client* needs a secret value for authentication.
Provide it directly through :envvar:`scimServer.auth.password` or use an existing Kubernetes Secret through :envvar:`scimServer.auth.existingSecret.name`.

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
     - Use HTTP Basic authentication for SCIM targets that don't support OIDC.
     - | :envvar:`scimServer.auth.basic.username`
       | :envvar:`scimServer.auth.password`
   * - ``bearer``
     - Use static Bearer token authentication for SCIM targets that don't support OIDC.
     - :envvar:`scimServer.auth.password`
   * - ``none``
     - Don't send an ``Authorization`` header.
     - No authentication values required.

When you use an existing Secret, the chart reads the entry named ``password`` by default.
If your Secret uses a different key, set :envvar:`scimServer.auth.existingSecret.keyMapping.password` to that key.
For example, :numref:`conf-scim-client-auth-secret-listing` uses a Bearer token stored under the key ``token`` in the ``scim-target-auth`` Secret.

.. code-block:: yaml
   :caption: Use a Bearer token from an existing Secret
   :name: conf-scim-client-auth-secret-listing

   scimServer:
     auth:
       method: "bearer"
       existingSecret:
         name: scim-target-auth
         keyMapping:
           password: token

.. _conf-scim-client-configuration-optional:

Optional values
---------------

You can override the following defaults in your :file:`scim-client-values.yaml` file.
:numref:`conf-scim-client-configuration-optional-listing` shows an example.

:envvar:`scimClient.config.logLevel`
  The log level for the *SCIM Client*.
  The default value is ``INFO``.

:envvar:`scimClient.config.prefill`
  Controls whether the provisioning subscription supplies existing user and user group data to the *SCIM Client* before sending new changes.
  The default value is ``true``.

:envvar:`scimClient.config.groupSync`
  Controls whether the *SCIM Client* provisions user groups.
  The default value is ``false``.

:envvar:`scimClient.config.externalIdUserMapping`
  The UDM attribute used for the SCIM ``externalId`` field of users.
  The default value is ``univentionObjectIdentifier``.

:envvar:`scimClient.config.externalIdGroupMapping`
   The UDM attribute used for the SCIM ``externalId`` field of user groups.
   The default value is ``univentionObjectIdentifier``.

:envvar:`scimServer.auth.oidc.scopes`
   Only applies when :envvar:`scimServer.auth.method` is ``oidc``.
   A list of additional scopes to request when obtaining an OIDC access token for SCIM server authentication.
   The *SCIM Client* always automatically includes the ``openid`` scope.
   Use this option if the downstream SCIM server requires specific scopes in the access token.
   The default value is ``null``, which means that the *SCIM Client* doesn't use any additional scopes.

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
   To use different UDM source attributes for ``externalId``, adapt :envvar:`scimClient.config.externalIdUserMapping` and :envvar:`scimClient.config.externalIdGroupMapping`.

After you have prepared :file:`scim-client-values.yaml`, configure the :ref:`conf-scim-client-provisioning` in your Nubus values file.
