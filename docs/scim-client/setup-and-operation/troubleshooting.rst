.. SPDX-FileCopyrightText: 2025 Univention GmbH
..
.. SPDX-License-Identifier: AGPL-3.0-only

.. _scim-client-troubleshooting:

Troubleshooting
===============

For network errors reported as ``RequestNetworkException``,
the *SCIM Client* keeps the provisioning task pending
and pauses processing before retrying.
It retries after 5 seconds, then 10 seconds, then 15 seconds,
and so on, up to 20 minutes between attempts.
For other failures, it stores the task
and its error in the *morgue* for manual inspection.
The *SCIM Client* doesn't retry tasks in the morgue automatically.
The client continues processing other pending tasks.
Pending tasks remain in the database
and the *SCIM Client* processes them when it restarts.

To start troubleshooting, check the container logs for warnings and errors:

#. List the pods in the Nubus namespace to find the *SCIM Client* pod name.
   Replace ``<namespace>`` with your Nubus namespace.
   In the default installation, look for a pod name containing ``scim-client``.

   .. code-block:: console
      :caption: List pods in the Nubus namespace
      :name: scim-client-troubleshooting-pods-listing

      $ kubectl --namespace <namespace> get pods

#. Show the logs.
   Replace ``<namespace>`` with your Nubus namespace
   and ``<scim-client-pod>`` with the name of the *SCIM Client* pod.

   .. code-block:: console
      :caption: Show *SCIM Client* logs
      :name: scim-client-troubleshooting-logs-listing

      $ kubectl logs \
         -n <namespace> <scim-client-pod> \
         -c main

.. _scim-client-troubleshooting-verification:

Check provisioning
------------------

To check synchronization with the *SCIM target*,
you need permission to create and modify a test user in Nubus.
You also need access to find the user
and inspect its attributes in the *SCIM target*.

To check synchronization, follow these steps:

#. Create a test user in Nubus, for example through the *Management UI*.
   If you use a selection filter, set the corresponding property so that the client selects this user.

   For information about how to create a user,
   see :external+uv-nubus-manual:ref:`nubus-user-management-create-wizard`
   in :cite:t:`uv-nubus-manual`.

#. Find the user in the SCIM target's user interface
   or by using its documented search function.

#. In Nubus, change an attribute supported by the target,
   such as the user's display name,
   and confirm the change in the *SCIM target* application interface.

Allow time for the client to process each change.
Use the log command in :numref:`scim-client-troubleshooting-logs-listing` to follow processing.

At the default ``INFO`` log level,
the client emits the following message texts.
The log messages refer to client startup or individual objects.
They don't confirm that the *SCIM Client* has synchronized all users.
Use the :option:`univention-scim-connector-task-management show-item` command
to inspect the state of an affected object.

``All expected tables present``
   Confirms that the client found its required database tables.

``Created entry in old db`` or ``Updating entry in old db``
   Indicate that the client records an object's processed state.

``Create SCIM resource ...`` and ``Update SCIM resource ...``
   Announce requests before the *SCIM Client* sends them.
   These messages alone don't confirm successful processing.

.. _scim-client-troubleshooting-common-errors:

Common errors
-------------

Check the *SCIM Client* logs for error messages.
For failed provisioning tasks, also inspect the errors stored in the morgue.
The following entries describe common errors and checks for their causes.

HTTP ``401`` or ``403``
   Check which service rejected the request.
   For the *SCIM target*,
   check the authentication settings,
   the referenced secret, and key.
   For more information, see :ref:`scim-client-configuration-auth`.

   For the *Provisioning API*,
   check :envvar:`provisioningApi.auth.username`,
   :envvar:`provisioningApi.auth.password`,
   :envvar:`provisioningApi.auth.existingSecret.name`,
   and the registered subscription.
   For more information,
   see :ref:`scim-client-configuration-mandatory`.

   With OIDC authentication,
   also check the token URL, client ID, client secret, and scopes.
   For more information,
   see :ref:`scim-client-configuration-auth`.

HTTP ``400`` or ``409`` when writing a resource
   Read the target's error detail for missing required attributes or a name conflict.
   The client matches existing resources by ``externalId``,
   so an account with the same ``userName`` alone doesn't count as a match.
   Before you connect existing accounts,
   see :ref:`scim-client-target-integration-requirements-identifiers`.

Unexpected HTTP ``404`` or a connection error
   Check :envvar:`scimServer.connection.url`, including the SCIM path, hostname, and port.
   Confirm that the service is reachable from the *SCIM Client* container.

``Failed to initialize database. Shutting down.``
   Check :envvar:`scimClient.config.dbConnectionString` and the database connection error in the logs.
   The database must exist, be reachable, and allow the configured user to create the client tables.

.. _scim-client-troubleshooting-cli:

Monitor the current state from the command line
-----------------------------------------------

.. program:: univention-scim-connector-task-management

Use the task-management command-line interface to inspect the provisioning state:

* ``tasks``: pending changes that are waiting for synchronization by the *SCIM Client*.

* ``old``: the state of an item at the moment it was successfully synchronized.

* ``morgue``: failed tasks and their errors.

  The client doesn't actively process these tasks.
  You can examine them and decide how to proceed.
  For information,
  see :ref:`scim-client-troubleshooting-errors`.

Run the tool inside the *SCIM Client* container,
where ``PROVISIONING_DB`` is already configured, as shown in :numref:`scim-client-troubleshooting-cli-listing`.

.. code-block:: console
   :caption: List the task-management commands
   :name: scim-client-troubleshooting-cli-listing

   $ kubectl exec \
      -n <namespace> <scim-client-pod> \
      -c main -- \
       univention-scim-connector-task-management --help

Replace ``--help`` with one of the following actions.
To see the options for an action, append ``--help`` to the action.

:``OBJECT_ID``: The UDM ``univentionObjectIdentifier``.
:``TASK_ID``: The numeric database ID shown by :option:`search-tasks`.

.. option:: show-item --obj-id OBJECT_ID

   Show an object's last synchronized state, pending tasks, and stored errors.

.. option:: summarize-tasks

   Summarize pending tasks.

.. option:: summarize-morgue

   Summarize failed tasks.

.. option:: search-tasks --first

   Show the first pending task.
   To show all pending tasks, omit ``--first``.

.. option:: search-old --obj-id OBJECT_ID

   Show the last successfully synchronized state.

.. option:: search-morgue

   Show failed tasks and tracebacks.
   You can filter the results with ``--obj-id OBJECT_ID``.
   For information about how to retry failed tasks,
   see :ref:`scim-client-troubleshooting-errors`.

.. option:: retry-from-morgue --obj-id OBJECT_ID

   Copy matching failed changes back into the task queue.

.. option:: remove-from-morgue --obj-id OBJECT_ID

   Remove matching error entries, not objects in SCIM or UDM.

.. option:: move-task-to-morgue --task-id TASK_ID --error-msg "Manual investigation"

   Move a pending task aside for investigation.

.. _scim-client-troubleshooting-errors:

Retry failed tasks
------------------

A change to an object's attributes in Nubus results in a new task with updated data.
After a successful create or update,
the client removes the existing morgue entries for that object.

To investigate and manually retry an entry that remains in the morgue,
follow these steps:

#. Inspect the stored failure with :option:`search-morgue`.
   :numref:`scim-client-morgue-output-listing` shows a username conflict with a shortened traceback.
   The traceback describes the saved provisioning error.
   It doesn't indicate a failure of the task-management command.

   .. code-block:: console
      :caption: Example of a stored error in the morgue
      :name: scim-client-morgue-output-listing

      $ kubectl exec -n <namespace> <scim-client-pod> -c main -- \
          univention-scim-connector-task-management search-morgue \
          --obj-id 11111111-2222-4333-8444-555555555555
      DN: uid=alice,cn=users,dc=example,dc=org
      Object Identifier: 11111111-2222-4333-8444-555555555555
      UDM module: users/user
      ID (database): 1
      Error occurred: 2026-09-09 10:15:00
      Error: Traceback (most recent call last):
        ...
      httpx.HTTPStatusError: Client error '400 Bad Request' for url 'https://scim.example.org/v2/Users'
      ...
      Request argument "dn" Object exists: (uid): The username is already in use as username or as groupname: alice.

      -

#. Fix the cause of the failure.

   .. warning::

      A retry uses the attributes saved with the failed task
      rather than current LDAP data
      and can overwrite newer data in the *SCIM target*.
      The task-management CLI doesn't display the attributes stored in the morgue.

#. Run :option:`retry-from-morgue` for the object
   to copy the failed changes back into the task queue.
   The client keeps the morgue entries
   until it successfully creates or updates the object.

   The client processes queued retries
   when it receives the next message, starts,
   or reaches an active network-retry iteration.
   To process them without waiting for a new message,
   restart an idle client and wait for the rollout
   with the commands in :numref:`scim-client-retry-restart-listing`.
   Replace ``<namespace>`` with your Nubus namespace.
   If you use a different deployment name,
   replace ``scim-client`` with that name.

   .. code-block:: console
      :caption: Restart the *SCIM Client* and wait for the rollout (example output)
      :name: scim-client-retry-restart-listing

      $ kubectl rollout restart deployment/scim-client --namespace <namespace>

      deployment.apps/scim-client restarted

      $ kubectl rollout status deployment/scim-client \
          --namespace <namespace> --timeout=180s

      deployment "scim-client" successfully rolled out

#. Run :option:`show-item --obj-id OBJECT_ID` to check the result.
   The example uses the deployment name to select the client pod after the restart.
   After a successful create or update,
   the output shows ``Synced as``, ``Currently no pending tasks``,
   and ``Currently no errors``,
   as shown in :numref:`scim-client-retry-success-output-listing`.

   ``Synced as`` alone describes the last successful synchronization.
   Recent pending tasks or error entries may still exist for the same object.
   Use :option:`search-old --obj-id OBJECT_ID` to verify that the stored attributes match the expected synchronized state.

   .. code-block:: console
      :caption: Example of a successfully retried item
      :name: scim-client-retry-success-output-listing

      $ kubectl exec -n <namespace> deployment/scim-client -c main -- \
          univention-scim-connector-task-management show-item \
          --obj-id 11111111-2222-4333-8444-555555555555
      Searching for 11111111-2222-4333-8444-555555555555
      Synced as uid=alice,cn=users,dc=example,dc=org (11111111-2222-4333-8444-555555555555; users/user; old:1)
      Currently no pending tasks
      Currently no errors

Use :option:`remove-from-morgue` to discard error entries you no longer need.
The client still processes later UDM changes to the object normally.

Use :option:`move-task-to-morgue` to move a pending task to the morgue for manual investigation.
Moving a task doesn't cancel a request
that the client has already sent to the SCIM target.
If the client is waiting before retrying,
it checks the task queue again only after that wait ends.

.. _scim-client-troubleshooting-support:

Information for support
-----------------------

Before you contact Univention support,
collect the client version, relevant logs and tracebacks,
and the affected object's :option:`show-item` output.
Include the steps to reproduce the problem and describe the expected behavior.
Redact credentials and sensitive data before sharing.
