.. SPDX-FileCopyrightText: 2026 Univention GmbH
..
.. SPDX-License-Identifier: AGPL-3.0-only

.. _conf-scim-client-integration:

Integrating a SCIM target
=========================

This chapter is for software vendors and developers who want to receive users and user groups from Nubus in their applications.
Your application provides the SCIM API; the *SCIM Client* sends provisioning requests to it.
The API uses SCIM 2.0 as defined in :rfc:`7643` and :rfc:`7644`.

For deployment and connection settings, see :ref:`conf-scim-client-configuration`.

.. _conf-scim-client-integration-api:

Resources and discovery
-----------------------

The *SCIM Client* provisions ``User`` resources.
It also provisions ``Group`` resources when the operator enables ``scimClient.config.groupSync``.
Group provisioning is disabled by default.
A target that receives only users doesn't need to provide group provisioning.

Configure the SCIM base URL, for example ``https://scim.example.com/scim/v2/``, in ``scimServer.connection.url``.
The paths in this chapter are relative to that URL.

When establishing the connection, the client queries the following discovery endpoints:

* ``/ResourceTypes`` describes the available resource types, their endpoints, and schema extensions.
* ``/Schemas`` describes their attributes, including whether attributes are writable or required.
* ``/ServiceProviderConfig`` describes capabilities such as filtering and authentication methods.

Advertise the resources and attributes that your application supports.
The client uses the discovered schemas and attribute mutability to build requests.
It logs warnings when it can't discover capabilities or the target doesn't advertise a capability it needs.
For the supported attributes and extensions, see :ref:`conf-scim-client-schemas`.

.. _conf-scim-client-integration-auth:

Authentication
--------------

The following methods authenticate the *SCIM Client* to your application's SCIM API.
The operator selects the authentication method through ``scimServer.auth.method``.
The client supports the following methods:

* ``bearer``: Send a configured token in the ``Authorization: Bearer <token>`` header.
* ``oidc``: Obtain an access token from the configured token endpoint using the client credentials grant, then send it as a Bearer token to the SCIM API.
* ``basic``: Send an HTTP Basic authentication header with the configured username and password.
* ``none``: Send no authentication header, for use in a test environment.

Support the method selected for your integration and advertise it in ``authenticationSchemes`` in ``/ServiceProviderConfig``.
The client checks for ``oauthbearertoken`` for both ``bearer`` and ``oidc``, and ``httpbasic`` for ``basic``.
For the corresponding Helm values and Secret configuration, see :ref:`conf-scim-client-configuration-auth`.

.. _conf-scim-client-integration-operations:

Resource operations
-------------------

The client sends requests with ``Accept: application/scim+json`` and ``Content-Type: application/scim+json``.
:numref:`conf-scim-client-integration-operations-table` shows the user operations and their expected success responses.
The client uses the same operations for groups when group provisioning is enabled.

.. list-table:: User operations
   :name: conf-scim-client-integration-operations-table
   :header-rows: 1
   :widths: 2 4 3

   * - Purpose
     - Request
     - Expected response
   * - Find an existing user
     - ``GET /Users?filter=...``
     - ``200 OK`` with a SCIM ``ListResponse``
   * - Create a user
     - ``POST /Users``
     - ``201 Created``
   * - Update a user
     - ``PUT /Users/{id}``
     - ``200 OK``
   * - Delete a user
     - ``DELETE /Users/{id}``
     - ``204 No Content``

Updates replace the resource with a representation built from the current Nubus data.
The client uses ``PUT``, not ``PATCH``.
It doesn't merge additional writable attributes from the target into the replacement request.

For a user that remains selected for provisioning, the client maps the Nubus ``disabled`` property to the inverse SCIM ``active`` value.
A change to ``disabled: true`` therefore produces an update with ``active: false`` when the target supports that writable attribute.
It doesn't produce a delete request.

The client requests deletion when the source object is deleted or no longer matches the configured selection filter.
For the filter settings, see :ref:`conf-scim-client-configuration-selection`.
If the resource is already absent from the target's lookup results, no delete request is needed.

.. _conf-scim-client-integration-identifiers:

Matching existing users and groups
----------------------------------

The client uses three identifiers for different purposes:

* ``externalId`` connects a target resource to its source object in Nubus.
  By default, its value is the Nubus ``univentionObjectIdentifier``.
* ``id`` is assigned by the SCIM target.
  The client uses the returned ``id`` in update and delete requests.
* ``userName`` is the user's login name.
  By default, it comes from the Nubus ``username`` property.

Before creating, updating, or deleting a resource, the client searches for its ``externalId``.
For example, it sends the following filter as the URL-encoded ``filter`` query parameter on ``/Users``::

   externalId eq "11111111-2222-4333-8444-555555555555"

The target must support this equality filter and return a SCIM ``ListResponse`` containing ``totalResults`` and ``Resources``.
Return the target-assigned ``id`` and the stored ``externalId`` in each matching resource.
:numref:`conf-scim-client-integration-lookup-listing` shows a shortened example of a matching response.

.. code-block:: json
   :caption: Lookup response for an existing user (shortened)
   :name: conf-scim-client-integration-lookup-listing

   {
     "schemas": ["urn:ietf:params:scim:api:messages:2.0:ListResponse"],
     "totalResults": 1,
     "Resources": [
       {
         "schemas": ["urn:ietf:params:scim:schemas:core:2.0:User"],
         "id": "target-user-id",
         "externalId": "11111111-2222-4333-8444-555555555555",
         "userName": "alice"
       }
     ]
   }

If no resource matches, the client creates one when processing a source object selected for provisioning.
With one match, it updates that resource.
Multiple matches cause an error.

The client doesn't automatically adopt an existing account with the same ``userName`` and a different or missing ``externalId``.
Such an account can cause a name conflict when the client attempts to create the resource.
For an existing account that should receive updates, arrange for its ``externalId`` to match the configured source identifier before provisioning it.

.. _conf-scim-client-integration-payload:

Example user data
-----------------

:numref:`conf-scim-client-integration-user-listing` shows a shortened create request body for a target that supports the corresponding core attributes.
The available Nubus properties and the target's schema determine the attributes in an actual request.

.. code-block:: json
   :caption: Example user create request body
   :name: conf-scim-client-integration-user-listing

   {
     "schemas": ["urn:ietf:params:scim:schemas:core:2.0:User"],
     "externalId": "11111111-2222-4333-8444-555555555555",
     "userName": "alice",
     "active": true,
     "name": {
       "givenName": "Alice",
       "familyName": "Example",
       "formatted": "Alice Example"
     },
     "displayName": "Alice Example",
     "emails": [
       {
         "value": "alice@example.org",
         "type": "mailbox",
         "primary": false
       }
     ]
   }

The target assigns ``id`` and ``meta``; the client omits them from create requests.
For the complete mapping of supported attributes and optional extensions, see :ref:`conf-scim-client-schemas`.

.. _conf-scim-client-integration-wire:

Wire connection example
-----------------------

Wire's `user provisioning documentation <https://docs.wire.com/latest/understand/single-sign-on/understand/main.html#user-provisioning-scimldap>`_ explains how to obtain a SCIM token and prepare your Wire team.

:numref:`conf-scim-client-integration-wire-listing` shows connection settings for Wire Cloud with user group provisioning disabled.
Add these settings to :file:`scim-client-values.yaml` and keep the Nubus and database settings described in :ref:`conf-scim-client-configuration`.
Create a Kubernetes Secret named ``scim-target-auth`` with the Wire SCIM token under the key ``token``, or adapt the Secret name and key to your existing Secret.
For a self-hosted Wire deployment, replace the URL with its SCIM API URL.

.. code-block:: yaml
   :caption: Wire Cloud connection settings for user provisioning
   :name: conf-scim-client-integration-wire-listing

   scimClient:
     config:
       groupSync: false

   scimServer:
     connection:
       url: "https://prod-nginz-https.wire.com/scim/v2"
     auth:
       method: "bearer"
       existingSecret:
         name: scim-target-auth
         keyMapping:
           password: token

Before installation, set ``scimClient.config.externalIdUserMapping`` to the UDM property that provides the identifier required by your Wire sign-in setup:

* For SAML single sign-on, the mapped ``externalId`` must match the user's SAML ``NameID``.
* For email and password authentication, the mapped ``externalId`` must be the user's email address.
  For example, set ``scimClient.config.externalIdUserMapping`` to ``mailPrimaryAddress`` if that UDM property contains the user's Wire login address.

Make sure that the selected Nubus users also meet Wire's requirements for user names and display names in its provisioning documentation.
