# Milestone 3: Asynchronous writes to UDM

[[_TOC_]]

## Goals

Goals of this development stage:

- Verification of the SCIM <-> UDM mapping.
- Verification of the UDM business rules implementation in the SCIM server.
- Performance tests show final performance.

## Result

- SCIM reads still go directly to the SCIM DB.
  - The SCIM service's availability and performance for read operations is independent of UDM.
- SCIM writes now go directly to the SCIM DB.
  - The SCIM service's availability and performance for write operations is independent of UDM.
- UDM business rules exist in _both_ UDM and SCIM server.
- There is no single source of truth anymore.
  - The SCIM and UDM REST APIs are independent services.
  - Changes to data model and business logic must be applied to _both_ services.
    - This raises the maintenance effort. To counter that, refactorings with the goal of a common code base should be evaluated.
- Changes done to SCIM are synchronized to the UDM DB asynchronously.
- Changes done to UDM are synchronized to the SCIM DB asynchronously.
- Errors encountered by either consumer are logged
  and sent to the Provisioning with realm `sync-error` and topic `scim2udm` or `udm2scim`,
  encoded as SCIM errors (see [RFC 7644 section 3.12](https://datatracker.ietf.org/doc/html/rfc7644#section-3.12)).
- Data in the SCIM and UDM databases is _eventually_ consistent.
- Performance tests show an excellent performance.
  - Read performance unchanged from MS1.
  - Write performance is almost back to that of MS1.
    - Difference is time needed by the business rules in the SCIM server.
  - Measure SCIM <-> UDM database synchronization delay.
    - Delay is the write performance of MS2 (in the respective direction) plus the delay of the Provisioning stack.
    - The delay of the Provisioning stack from SCIM to UDM is lower (single digit ms) than from UDM to SCIM,
      because SCIM events do not need to be processed by the UDM Transformer.

## Concurrent write conflict resolution using attribute-level comparisons

Please see section of same name in [Milestone 2: Synchronous writes to UDM, reads from SQL](milestone2.md).
The only difference in MS3 is, that this must now also happen in the _SCIM 2 UDM Consumer_.

## Handling password (hashes)

Questions:

- How can we handle the clear text password with asynchronous interaction with UDM?
  - Store it in the event?
  - Or make the call synchronous?
  - ...

- How can we handle passwords which do not match the given complexity policies?
  - Copy code from UDM?
  - Make a synchronous call to UDM?
  - Extract password policy handling from UDM into dedicated RPC service?

## Components overview

![Components overview](images/components-ms3-overview.png "Components overview")

## Sequence diagram: Reading from SCIM REST API

![Sequence diagram (milestone 3): Reading from SCIM REST API](images/sequence-ms23-scim-read.png "Sequence diagram (milestone 3): Reading from SCIM REST API")

## Writing to SCIM REST API

### Components

![Components involved when writing to SCIM REST API](images/components-ms3-scim-write.png "Components involved when writing to SCIM REST API")

### Sequence diagram

![Sequence diagram: Writing to SCIM REST API](images/sequence-ms3-scim-write.png "Sequence diagram: Writing to SCIM REST API")

## Writing to UDM REST API

### Components

![Components writing to UDM REST API (milestone 3)](images/components-ms3-udm-write.png "Components writing to UDM REST API (milestone 3)")

### Sequence diagram

![Sequence diagram (milestone 3): Writing to UDM REST API](images/sequence-ms23-udm-write.png "Sequence diagram (milestone 3): Writing to UDM REST API")

## Sequence diagram: UDM 2 SCIM Consumer

![Sequence diagram (milestone 3): UDM 2 SCIM Consumer](images/sequence-ms3-udm-2-scim-consumer.png "Sequence diagram (milestone 2): UDM 2 SCIM Consumer")

## Sequence diagram: SCIM 2 UDM Consumer

![Sequence diagram (milestone 3): SCIM 2 UDM Consumer](images/sequence-ms3-scim-2-udm-consumer.png "Sequence diagram (milestone 3): SCIM 2 UDM Consumer")

## Authentication

Unchanged from MS1:

- The SCIM database's connection settings are read from the environment.
  Secrets (passwords, certificates etc.) are read from files whose paths are in environment variables.

Unchanged from MS2:

- To use the SCIM REST API the client must send an OAuth token with the request.
  - A certificate to verify the OAuth tokens is provided as a (bind mounted) file.
  - The path to the certificate file can be read from an environment variable.
- The user in the token must exist in the SCIM database.
- The user must be member of a certain group in the SCIM DB.
  - The groups name is configurable through an environment variable and defaults to `scim-clients`.
- The user should exist in UDM/LDAP and will be created in the SCIM DB by the UDM 2 SCIM Consumer.
- The SCIM server's container offers a CLI to create-or-update users and groups in the SCIM database.
  - This can be used for testing without an associated user synchronized from UDM.
  - This must be used to create the user that the UDM 2 SCIM Consumer uses.
- The UDM 2 SCIM Consumer reads the SCIM REST API's connection settings from the environment.
  Secrets (passwords, certificates etc.) are read from files whose paths are in environment variables.

Changed from MS2:

- The SCIM REST server _doesn't_ read the UDM REST API's connection settings anymore.

New:

- The SCIM 2 UDM Consumer reads the UDM REST API's connection settings from the environment.
  Secrets (passwords, certificates etc.) are read from files whose paths are in environment variables.
  - The LDAP account (the "bind dn") is configurable.
  - As BSI base security expects the password to be rotated, the `cn=admin` account shouldn't be used.
    Thus, a dedicated service account should be created.
  - For performance reasons, the account should profit from permissive LDAP ACLs.

## Authorization

Unchanged from MS1:

- Restrictions defined in the SCIM RFCs apply (e.g., the `id` field is read-only).

Changed from MS2:

- Restrictions in the UDM data model and business logic apply,
  when changes are forwarded _asynchronously_ by the SCIM 2 UDM Consumer.
  - UDM REST API error messages are logged and sent to the Provisioning.

New:

- Restrictions in the UDM data model and business logic apply,
  when changes are verified by the SCIM server,
  as UDMs business logic has been copied into the SCIM service.

## Deliverables

No change to MS2.

## Navigation

- Previous chapter: [Milestone 2: Synchronous writes to UDM, reads from SQL](milestone2.md)
