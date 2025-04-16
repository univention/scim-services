# Milestone 2: Synchronous writes to UDM, reads from SQL

[[_TOC_]]

This stage introduces synchronization between SCIM and UDM.

- SCIM and UDM read directly from their respective databases.
- Writes to SCIM are synchronously forwarded to the UDM database.
- Writes to UDM are asynchronous forwarded to the SCIM database.

Having separate code paths for reading and writing is an application of the CQRS pattern,
described in a section below.

## Goals

Goals of this development stage:

- Verification of the service's conformity to SCIM RFCs - for the whole set of features and attributes
  that Univention wants to support.
- Verification of the [UDM <-> SCIM mapping](../udm-scim-mapping.md), including custom schema extensions.
  - "Univention" schema extensions for users and groups are created.
    They contain attributes for default UDM properties without SCIM equivalent in the default SCIMv2 schemas
    (`User`, `Group`, and `Enterprise User`).
  - An additional user schema extension is created for an example application with a few attributes,
    e.g. `isMyAppEnabled` (boolean) and `myAppValue` (float).
    This extension schema is for testing and demonstrating (documenting) our solution, not for production.
- The SCIM schema and the SCIM<->UDM mapping are configurable.
  - An interface for changing the default configuration is not exposed for now.
  - It is OK if a restart of the service is required to change the configuration.
- Tests verify compatibility with the Entra ID SCIM client ("Microsoft Entra provisioning service")
  using the service's default or a documented custom configuration.
- Explore effects of UDM model and business rules on SCIM service and client.
  - Verification of the service's conformity to SCIM RFCs
  - Add changed behavior and possible SCIM-non-conformity to public documentation.
  - Write tests that verify the expected behavior.
    - Writing to SCIM: handling of UDM value limitations, sync to UDM (successes and errors)
    - Writing to UDM: sync to SCIM DB
- Performance tests measure the expected write performance degradation.
- The documentation contains the SCIM<->UDM mapping and, if possible, how it can be configured.
- The documentation explains how custom schema extensions can be added to the SCIM service.
  This includes the SCIM schema, SQL schema, and the SCIM<->UDM mapping.
- The service can be used in production.
  That means the customer's functional and non-functional requirement are met.
  - It is OK if functional and non-functional requirement desired for the product are missing or need improving.
  - A roadmap for the implementation of those and of MS3 should be created.

## Result

- SCIM reads still go directly to the SCIM DB.
  - The SCIM service's availability and performance for read operations is independent of UDM.
- SCIM writes now go _first_ to the UDM REST API.
  The resulting UDM object is then transformed (mapped) to a SCIM object, which is written to the SCIM DB.
  - The SCIM service's availability and performance for write operations is dependent on UDMs.
  - UDM model and business rules exist only in UDM.
  - UDM business rules are exposed by SCIM service.
    E.g. when a request is denied because of a missing or malformed value or reference.
  - UDM is the single source of truth.
- Changes done to UDM are synchronized to the SCIM DB asynchronously.
  - The SCIM server does not forward change requests started by UDM back to UDM, preventing a loop.
- Errors encountered by the UDM 2 SCIM Consumer are logged.
- Synchronization conflict resolution happens on the attribute level.
  There are a few problematic scenarios (see section _Concurrent write conflict resolution using attribute-level comparisons_).
  Situations where a conflict on the attribute level is detected are logged at level `INFO` or `WARNING`.
- The UDM REST API and SCIM API use the same backend for locking during the creation of globally unique values
  like username and email addresses.
  - If we were to implement a locking mechanism today, we wouldn't use UDM or LDAP.
    They are too slow, lack atomic functions and automatic cleanup.
    Redis, etcd and memcached come to mind.
  - We split a decision about a new locking backend from the implementation of the SCIM service and
    start with the existing one in UDM (maybe moved into a common Python library).
- Data in the SCIM and UDM databases is _eventually_ consistent.
- Performance tests show an unchanged SCIM read performance, and a sever write performance degradation.
  - Read performance is unchanged from MS1.
  - Write performance is even lower than the UDM REST API, because the write time from MS1 for the SCIM backend is added.
  - Delay between SCIM and UDM databases depends on the direction.
    - No SCIM to UDM database synchronization delay.
    - UDM to SCIM database synchronization delay is the Provisioning latency plus the write time from MS1 for the SCIM REST API.
    - KPIs like, e.g., 250ms after a UDM object was CUD, the SCIM object is synchronized, do not exist.
      So, we measure the latency now, and use it as a default for the future.

## Command and Query Responsibility Segregation (CQRS)

TODO: provide a summary

Please head over to [this article](https://dtroeder.gitpages.knut.univention.de/future-of-nubus/cqrs.html)
on the Command and Query Responsibility Segregation (CQRS) pattern.

## Eventual consistency

TODO: provide a summary

Please head over to [this article](https://dtroeder.gitpages.knut.univention.de/future-of-nubus/ucsschool-software-architecture.html#eventual-consistency)
on eventual consistency.

## Concurrent write conflict resolution using attribute-level comparisons

There are situations in which the same object is changed "simultaneously" by a UDM and a SCIM client.
"Simultaneous" in this context means that both objects are changed, before they are synchronized.

Example: The object "A" exists in UDM and SCIM.
When it is changed in the UDM DB, an event is sent, so the modification is also applied to "A" in the SCIM DB.
But before that happens, the object "A" is changed in the SCIM DB by a SCIM client.

If we'd decided on an object level which change to accept, we'd lose one change.
In the above example we'd lose the UDM change, because we'd keep the newer SCIM object.

### Simultaneous updates

Although we don't have versioned attributes, we can still do a finer-grained synchronization:
UDM and SCIM change events contain the previous ("old") and the "new" state of an object, including the attributes.
We can calculate the "difference": The attributes that changed in the source object (in the example UDM).
Then we overwrite only those changed attributes on the target object (in the example SCIM).

This "delta" synchronization mode handles all update situations safely except for one:
The same attribute was changed on the same object "simultaneously" in UDM and SCIM.

- Very unlikely, because most attributes are written by only one application,
  and that application won't use both interfaces (SCIM and UDM).
- The situation won't be detected.
  An automatic conflict resolution is not possible.
  The value from the last or slowest object to synchronize will overwrite the other.

#### Handling multi-value fields

Multi-value fields (attributes where the value is a list of values) must be handled by applying changes,
instead of overwriting the whole attribute.

That means, that an update of a multi-value field is done in two steps:

1. Removing items from the list on the target attribute that were removed from the "old" attribute (compared to "new").
2. Adding items to the list on the target attribute that were added to the "new" attribute (compared to "old").

### Simultaneous creations

If we want, the "delta" synchronization mode can handle the following situation automatically.
But maybe we want to interpret the situation as a conflict the operator has to handle.
**→ Needs discussion.**

Two objects with the same values in attributes with uniqueness constraints can be created "simultaneously" by SCIM and UDM,
e.g. a user or a group with the same name.
(The same UUID is statistically improbable.)

- Very unlikely, because the provisioning of users and groups usually follows the organizational requirements of the customer,
  with only one "input channel" for identities (UCS@school import, AD Connector, interactively).
  Event when multiple channel are used, the user sets usually don't overlap
  (e.g. teachers come from the AD, students come from a UCS@school import).
- It is more likely to happen for groups than for users.
- When a "simultaneous" creation happens, it can be detected.
  An automatic conflict resolution is possible, but may not be desirable.
  My proposal (see "Sequence diagram: UDM 2 SCIM Consumer") is an "optimistic" resolution:
  When the synchronization code detects an existing object, it updates it.
  Reasoning: Using the same identifier (name) for an object usually means it's the same object.
- There is a corner case that cannot (and IMHO should not) be solved automatically:
  Objects with multiple uniqueness constraints (e.g. `username` and `mailPrimaryAddress`) with differing values.
  Reasoning: This is a clear indicator of an organizational error (e.g. parallel imports with different configurations).

## Handling password (hashes)

"Password" is a default attribute in SCIM.
If it is given, it needs to be passed on to UDM, so users are usable.

The SCIM service itself does not need a password or password hash for authentication,
because OAuth is used and the authentication is done by the IdP.
The password or hash can never be read through SCIM.
So, the is no need to store the password or a password hash in the SCIM DB.

## Components overview

![Components overview (milestone 2)](images/components-ms2-overview.png "Components overview (milestone 2)")

## Sequence diagram: Reading from SCIM REST API

![Sequence diagram (milestone 2): Reading from SCIM REST API](images/sequence-ms23-scim-read.png "Sequence diagram (milestone 2): Reading from SCIM REST API")

## Writing to SCIM REST API

### Components

![Components writing to SCIM REST API (milestone 2)](images/components-ms2-scim-write.png "Components writing to SCIM REST API (milestone 2)")

### Sequence diagram

![Sequence diagram (milestone 2): Writing to SCIM REST API](images/sequence-ms2-scim-write.png "Sequence diagram (milestone 2): Writing to SCIM REST API")

## Writing to UDM REST API

### Components

![Components writing to UDM REST API (milestone 2)](images/components-ms2-udm-write.png "Components writing to UDM REST API (milestone 2)")

### Sequence diagram

![Sequence diagram (milestone 2): Writing to UDM REST API](images/sequence-ms23-udm-write.png "Sequence diagram (milestone 2): Writing to UDM REST API")

## Sequence diagram: UDM 2 SCIM Consumer

![Sequence diagram (milestone 2): UDM 2 SCIM Consumer](images/sequence-ms2-udm-2-scim-consumer.png "Sequence diagram (milestone 2): UDM 2 SCIM Consumer")

## Authentication

Unchanged from MS1:

- The SCIM REST server reads the UDM REST API's connection settings from the environment.
  Secrets (passwords, certificates etc.) are read from files whose paths are in environment variables.
  - The LDAP account (the "bind dn") is configurable.
  - As BSI base security expects the password to be rotated, the `cn=admin` account shouldn't be used.
    Thus, a dedicated service account should be created.
  - For performance reasons, the account should profit from permissive LDAP ACLs.
- To use the SCIM REST API the client must send an OAuth token with the request.
  - For details see [section "Authentication" of the overview page](Nubus-SCIM-service-architecture.md#authentication).

New:

- The SCIM database's connection settings are read from the environment.
  Secrets (passwords, certificates etc.) are read from files whose paths are in environment variables.
- To use the SCIM REST API the user in the token:
  - Must exist in the SCIM database.
  - Must be member of a certain group in the SCIM DB.
    - The groups name is configurable through an environment variable and defaults to `scim-clients`.
- The user should exist in UDM/LDAP and will be created in the SCIM DB by the UDM 2 SCIM Consumer.
- The SCIM server's container offers a CLI to create-or-update users and groups in the SCIM database.
  - This can be used for testing without an associated user synchronized from UDM.
  - This must be used to create the user that the UDM 2 SCIM Consumer uses.
- The UDM 2 SCIM Consumer reads the SCIM REST API's connection settings from the environment.
  Secrets (passwords, certificates etc.) are read from files whose paths are in environment variables.

## Authorization

Unchanged from MS1:

- Restrictions defined in the SCIM RFCs apply (e.g., the `id` field is read-only).
- Restrictions in the UDM data model and business logic apply,
  when changes are forwarded _synchronously_ by the SCIM server.
  The SCIM server returns UDM errors to the SCIM client.
  - UDM REST API error messages are transformed to SCIM error messages that adhere to
    [RFC 7644 section 3.12](https://datatracker.ietf.org/doc/html/rfc7644#section-3.12).

New:

- The client/user in the token must exist as a user object in the SCIM (SQL) DB and
  must be member of a certain group object in the SCIM DB.
  - For details see [section "Authorization" of the overview page](Nubus-SCIM-service-architecture.md#authorization).

## Deliverables

No change to MS1.

## Navigation

- Previous chapter: [Milestone 1: Milestone 1: Minimal viable product | Synchronous adapter in front of UDM](milestone1.md)
- Next chapter: [Milestone 2.1: Metrics, Provisioning, ...](milestone2.1.md)
