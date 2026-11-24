.. SPDX-FileCopyrightText: 2026 Univention GmbH
..
.. SPDX-License-Identifier: AGPL-3.0-only

.. _scim-client-target-integration-requirements:

SCIM target integration requirements
====================================

This page is for software vendors and software developers
who want to receive users and user groups from Nubus in their applications.
Your application provides the SCIM API
using SCIM 2.0 as defined in :rfc:`7643` and :rfc:`7644`.
The *SCIM Client* sends provisioning requests to it.

For deployment and connection settings, see :ref:`scim-client-configuration`.

.. _scim-client-target-integration-requirements-api:

Resources and discovery
-----------------------

The *SCIM Client* provisions ``User`` resources
and ``Group`` resources if the operator enables :envvar:`scimClient.config.groupSync`.
By default, the *SCIM Client* doesn't provision groups.
Group provisioning is experimental.
A target that receives only users doesn't need to provide group provisioning.
For more information,
see :ref:`scim-client-configuration-selection`.

Configure the SCIM base URL,
for example ``https://scim.example.com/scim/v2/``,
in :envvar:`scimServer.connection.url`.
The paths on this page are relative paths to the URL in :envvar:`scimServer.connection.url`.

When the client establishes a connection,
it queries the following discovery endpoints:

``/ResourceTypes``
   Describes the available resource types, their endpoints, and schema extensions.

``/Schemas``
   Describes their attributes, including whether attributes are writable or required.

``/ServiceProviderConfig``
   Describes capabilities such as filtering and authentication methods.

Advertise the resources and attributes that your application supports.
The client uses the discovered schemas and attribute mutability to build requests.
It logs warnings when it can't discover capabilities
or the target doesn't advertise a capability it needs.
If a network failure occurs during startup,
the client attempts discovery again during task processing.
Other discovery errors can prevent the client from starting.
For the supported attributes and extensions, see :ref:`scim-client-schemas`.

.. _scim-client-target-integration-requirements-auth:

Authentication
--------------

The following methods authenticate the *SCIM Client* to your application's SCIM API.
The operator selects the authentication method through :envvar:`scimServer.auth.method`.

The client supports the following methods:

:``bearer``: Send a configured token in the :samp:`Authorization: Bearer {TOKEN}` header.
   Replace ``TOKEN`` with the configured bearer token.

:``oidc``: Obtain an access token from the configured token endpoint
   using the client credentials grant, then send it as a Bearer token to the SCIM API.

:``basic``: Send an HTTP Basic authentication header with the configured username and password.

:``none``: Send no authentication header, for use in a test environment.

Support the method selected for your integration
and advertise it in ``authenticationSchemes`` through the ``/ServiceProviderConfig`` URL.
The client checks ``oauthbearertoken`` for both ``bearer`` and ``oidc``,
and ``httpbasic`` for ``basic``.

For the corresponding Helm Chart values and secret configuration, see :ref:`scim-client-configuration-auth`.

.. _scim-client-target-integration-requirements-operations:

Resource operations
-------------------

The client sends requests with the headers ``Accept: application/scim+json`` and ``Content-Type: application/scim+json``.
:numref:`scim-client-target-integration-requirements-operations-table`
shows the user operations and their expected success responses.
The client uses the same operations for groups
if the client has group provisioning enabled.

Updates replace the resource with a representation built from the Nubus object data.
The client uses ``PUT``, not ``PATCH``.
It doesn't merge additional writable attributes from the target into the replacement request.

.. _scim-client-target-integration-requirements-operations-table:

.. list-table:: User operations
   :header-rows: 1
   :widths: 3 4 5

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

.. _scim-client-target-integration-requirements-user-states:

User account states
-------------------

For a user that remains selected for provisioning,
the client maps the ``disabled`` property
from the Univention Directory Manager (UDM) object in Nubus
to the inverse SCIM ``active`` value.
A change to ``disabled: true``
therefore produces an update with ``active: false``
when the target supports that writable attribute.
It doesn't produce a delete request.

The client requests deletion
when the source object is deleted
or no longer matches the configured selection filter.

For the filter settings, see :ref:`scim-client-configuration-selection`.
If the resource is already absent from the target's lookup results, no delete request is needed.

Univention recommends the behavior in :numref:`scim-client-target-integration-requirements-user-states-table`
for user accounts provisioned from Nubus.
For these user accounts,
the application should treat Nubus as the authoritative source of account data.
It shouldn't create or change these accounts independently.

.. _scim-client-target-integration-requirements-user-states-table:

.. list-table:: Recommended handling of user account states
   :header-rows: 1
   :widths: 1 3 8

   * - State
     - SCIM value or request
     - Application behavior

   * - Active
     - ``active: true``
     - Allow the user to sign in and use the application.

   * - Deactivated
     - ``active: false``
     - Prevent sign-in and keep the user's data.

   * - Deleted
     - :samp:`DELETE /Users/{{id}}`
     - Remove the user account and its personal data according to the application's own deletion rules.

.. _scim-client-target-integration-requirements-identifiers:

Matching existing users and groups
----------------------------------

The client uses three identifiers for different purposes:

``externalId``
   Connects a target resource to its source object in Nubus.

   :Default value: ``univentionObjectIdentifier`` in Nubus

``id``
   The *SCIM target* assigns ``id``.
   The *SCIM Client* uses the returned ``id`` in update and delete requests.

``userName``
   Is the user's sign-in name.
   By default, it comes from the Nubus ``username`` property.

Before the *SCIM Client* creates, updates, or deletes a resource,
it searches for its ``externalId``.
For example,
it sends the filter in :numref:`scim-client-target-integration-requirements-identifiers-external-id-listing`
as the URL-encoded ``filter`` query parameter on ``/Users``.

.. code-block::
   :caption: Example filter for an ``externalId`` lookup
   :name: scim-client-target-integration-requirements-identifiers-external-id-listing

   externalId eq "11111111-2222-4333-8444-555555555555"

The target must accept ``externalId`` when creating a resource.
It must also support this equality filter
and return a SCIM ``ListResponse`` that contains ``totalResults`` and ``Resources``.
Return the target-assigned ``id`` and the stored ``externalId`` in each matching resource.
:numref:`scim-client-integration-lookup-listing` shows a shortened example of a matching response.

.. code-block:: json
   :caption: Lookup response for an existing user (shortened)
   :name: scim-client-integration-lookup-listing

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

If no resource matches,
the client creates a resource when it provisions a source object.
With one match, it updates the resource when it provisions the source object.
It deletes the resource when a technical administrator deletes the source object
or when the source object no longer matches the selection filter.
Multiple matches cause an error.

The client doesn't automatically adopt an existing account with the same ``userName``
and a different or missing ``externalId``.
Such an account can cause a name conflict
when the client attempts to create the resource.
For an existing account that should receive updates,
arrange for its ``externalId`` to match the configured source identifier before provisioning it.

.. _scim-client-target-integration-requirements-payload:

Example user data
-----------------

:numref:`scim-client-target-integration-requirements-payload-listing`
shows a shortened create request body for a target
that supports the corresponding core attributes.
The available Nubus properties and the target's schema determine the attributes in an actual request.

The target assigns ``id`` and ``meta``.
The client omits them from create requests.
For the complete mapping of supported attributes and optional extensions,
see :ref:`scim-client-schemas`.

.. code-block:: json
   :caption: Example user create request body
   :name: scim-client-target-integration-requirements-payload-listing

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
         "primary": true
       }
     ]
   }

.. _scim-client-target-integration-requirements-example-wire:

Wire connection example
-----------------------

This example uses *Wire Messenger* to illustrate
how the *SCIM target* requirements apply to client configuration.
It shows Bearer authentication for user provisioning
and how to choose an ``externalId`` mapping for *Wire Messenger* sign-in.

The Wire `user provisioning documentation <https://docs.wire.com/latest/understand/single-sign-on/understand/main.html#user-provisioning-scimldap>`_
explains how to obtain an SCIM token and prepare your Wire team.

:numref:`scim-client-target-integration-requirements-example-wire-listing`
shows connection settings for *Wire Messenger* that deactivates group provisioning.
To use this example,
add these settings to :file:`scim-client-values.yaml`
and keep the Nubus and database settings described in :ref:`scim-client-configuration`.
Create a Kubernetes secret named ``scim-target-auth``
with the Wire SCIM token under the key ``token``,
or adapt the secret name and key to your existing secret.
For a self-hosted Wire deployment, replace the URL with its SCIM API URL.
For installation and verification, see :ref:`scim-client-installation`.

.. code-block:: yaml
   :caption: Wire connection settings for user provisioning
   :name: scim-client-target-integration-requirements-example-wire-listing

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

Before installation,
set :envvar:`scimClient.config.externalIdUserMapping` to the UDM property
that provides the identifier required by your Wire sign-in setup:

* For SAML single sign-on, the mapped ``externalId`` must match the user's SAML ``NameID``.
* For email and password authentication, the mapped ``externalId`` must be the user's email address.

  For example, set :envvar:`scimClient.config.externalIdUserMapping` to ``mailPrimaryAddress``
  if that UDM property contains the user's Wire sign-in address.

Make sure that the selected Nubus users
also meet the username and display name requirements
in Wire's provisioning documentation.
