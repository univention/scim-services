.. SPDX-FileCopyrightText: 2025 Univention GmbH
..
.. SPDX-License-Identifier: AGPL-3.0-only

.. _conf-scim-client-troubleshooting:

Troubleshooting
===============

For network errors reported as ``RequestNetworkException``, the *SCIM Client* keeps the provisioning task pending and pauses processing before retrying.
It retries after 5 seconds, then 10 seconds, then 15 seconds, and so on, up to 20 minutes between attempts.
For other failures, it stores the task and its error in the *morgue* for manual inspection.
Tasks in the morgue aren't retried automatically.
The client continues processing other pending tasks.
Pending tasks remain in the database and are processed when the client restarts.

Start by checking the container logs for warnings and errors, as shown in :numref:`conf-scim-client-troubleshooting-logs-listing`.
Replace ``<namespace>`` with your Nubus namespace and ``<scim-client-pod>`` with the name of the *SCIM Client* pod.

.. code-block:: console
   :caption: Show *SCIM Client* logs
   :name: conf-scim-client-troubleshooting-logs-listing

   $ kubectl logs -n <namespace> <scim-client-pod> -c main

.. _conf-scim-client-troubleshooting-cli:

Monitor the current state from the command line
-----------------------------------------------

.. program:: univention-scim-connector-task-management

Use the task-management command-line interface to inspect the provisioning state:

* ``tasks``: Pending changes waiting to be synchronized.
* ``old``: The state of an item at the moment it was successfully synchronized.
* ``morgue``: Failed tasks and their errors.
  The client doesn't actively process these tasks.
  You can examine them and decide how to proceed.

Run the tool inside the *SCIM Client* container, where ``PROVISIONING_DB`` is already configured, as shown in :numref:`conf-scim-client-troubleshooting-cli-listing`.

.. code-block:: console
   :caption: List the task-management commands
   :name: conf-scim-client-troubleshooting-cli-listing

   $ kubectl exec -n <namespace> <scim-client-pod> -c main -- \
       univention-scim-connector-task-management --help

Replace ``--help`` with one of the following actions.
Use ``<command> --help`` for its options.

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
   Omit ``--first`` to show all.

.. option:: search-old --obj-id OBJECT_ID

   Show the last successfully synchronized state.

.. option:: search-morgue

   Show failed tasks and tracebacks.
   Optionally filter with ``--obj-id OBJECT_ID``.

.. option:: retry-from-morgue --obj-id OBJECT_ID

   Copy matching failed changes back into the task queue.

.. option:: remove-from-morgue --obj-id OBJECT_ID

   Remove matching error entries, not objects in SCIM or UDM.

.. option:: move-task-to-morgue --task-id TASK_ID --error-msg "Manual investigation"

   Move a pending task aside for investigation.

.. _conf-scim-client-troubleshooting-errors:

Retry failed tasks
------------------

To investigate and retry a task in the morgue, follow these steps:

#. Inspect the stored failure with :option:`search-morgue`.
   :numref:`conf-scim-client-morgue-output-listing` shows a username conflict with a shortened traceback.
   The traceback describes the saved provisioning error.
   It doesn't indicate a failure of the task-management command.

   .. code-block:: console
      :caption: Example of a stored error in the morgue
      :name: conf-scim-client-morgue-output-listing

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

#. Fix the cause and check the task's stored attributes before retrying.
   The retry uses these attributes rather than fresh LDAP data.
   Make sure that they won't overwrite a more recent state.

#. Run :option:`retry-from-morgue` for the object to copy the failed changes back into the task queue.
   This keeps the morgue entries until the client successfully creates or updates the object.
   After a successful create or update, the client removes all morgue entries for that object.

   The client processes queued retries when it receives the next message, starts, or reaches an active network-retry iteration.
   To process them without waiting for a new message, restart an idle client.

#. Run :option:`show-item --obj-id OBJECT_ID` to check the result.
   After a successful create or update, the output shows ``Synced as``, ``Currently no pending tasks``, and ``Currently no errors``, as in :numref:`conf-scim-client-retry-success-output-listing`.

   .. code-block:: console
      :caption: Example of a successfully retried item
      :name: conf-scim-client-retry-success-output-listing

      $ kubectl exec -n <namespace> <scim-client-pod> -c main -- \
          univention-scim-connector-task-management show-item \
          --obj-id 11111111-2222-4333-8444-555555555555
      Searching for 11111111-2222-4333-8444-555555555555
      Synced as uid=alice,cn=users,dc=example,dc=org (11111111-2222-4333-8444-555555555555; users/user; old:1)
      Currently no pending tasks
      Currently no errors

   ``Synced as`` alone describes the last successful synchronization.
   Recent pending tasks or error entries may still exist for the same object.
   Use :option:`search-old --obj-id OBJECT_ID` to verify that the stored attributes match the expected synchronized state.

Use :option:`remove-from-morgue` to discard error entries you no longer need.
The client still processes later UDM changes to the object normally.

Use :option:`move-task-to-morgue` to move a pending task to the morgue for manual investigation.
Moving a task doesn't cancel a request that the client has already sent to the SCIM target.
If the client is waiting before retrying, it checks the task queue again only after that wait ends.

.. _conf-scim-client-troubleshooting-support:

Information for support
-----------------------

Before contacting support, collect the client version, relevant logs and tracebacks, and the affected object's :option:`show-item` output.
Include the steps to reproduce the problem and describe the expected behavior.
Redact credentials and sensitive data before sharing.
