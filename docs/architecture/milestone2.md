# Milestone 2: Synchronous writes to UDM, reads from SQL

[[_TOC_]]

This stage introduces a dedicated database for SCIM.

- SCIM and UDM read directly from their respective databases.
- Writes to SCIM are synchronously forwarded to the UDM database and copy afterward to the SCIM database.
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
- Performance tests measure the read and write performance change compared to MS1.
- The documentation updates the list of non-conforming parts of the SCIM service (missing attributes, operations, unusual behavior etc.).
- The documentation updates the SCIM<->UDM mapping and how it can be configured.
- The documentation explains how custom schema extensions can be added to the SCIM service.
  This includes the SCIM schema, SQL schema, and the SCIM<->UDM mapping.
- The service can be used in production.
  That means the customer's functional and non-functional requirement are met.
  - It is OK if some functional and non-functional requirement desired for the final product are missing or need improving,
    as long as the requirement of the initial customer are met.
  - A roadmap for the implementation of the missing functional and non-functional requirements and of MS3 is created.

## Result

- SCIM reads now go directly to the SCIM DB.
  - The SCIM service's availability and performance for read operations is independent of UDM.
- SCIM writes now go _first_ to the UDM REST API.
  The resulting UDM object is then transformed (mapped) to a SCIM object, which is written to the SCIM DB.
  - The SCIM service's availability and performance for write operations is dependent on UDM's.
  - UDM model and business rules exist only in UDM.
  - UDM business rules are exposed by SCIM service.
    E.g. when a request is denied because of a missing or malformed value or reference.
  - UDM is the single source of truth.
- Changes done to the UDM DB are synchronized to the SCIM DB asynchronously.
  - The SCIM server does not forward change requests started by UDM back to UDM, preventing a loop.
- Errors encountered by the UDM 2 SCIM Consumer are logged.
- Synchronization conflict resolution happens on the attribute level.
  There are a few problematic scenarios (see section _Concurrent write conflict resolution using attribute-level comparisons_).
  Situations where a conflict on the attribute level is detected are logged at level `INFO` or `WARNING`.
- The creation of globally unique values is done solely by UDM.
  Thus, no common locking mechanism is required yet.
  - SCIM's `id` field maps to UDM's `univentionObjectIdentifier`.
    Thus, the work on it is a prerequisite (see [Epic 880](https://git.knut.univention.de/groups/univention/-/epics/880)).
- Data in the SCIM and UDM databases is _eventually_ consistent.
- Performance tests show an improved SCIM read performance, and a slight write performance degradation.
  - Read performance has improved compared to MS1, because the SCIM DB schema is optimized for the SCIM service.
  - Write performance is even lower compared to MS1, because now two backends must write the data:
    the UDM backend and the SCIM backend.
  - Delay between SCIM and UDM databases depends on the direction.
    - No SCIM to UDM database synchronization delay.
    - UDM to SCIM database synchronization delay is the Provisioning latency plus
      the time to convert a UDM object to a SCIM representation and write it to the SCIM DB.
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
- Next chapter: [Milestone 2.1: Add metrics, provisioning](milestone2.1.md)
