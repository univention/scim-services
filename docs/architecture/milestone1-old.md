# Milestone 1: Standalone SCIM server

[[_TOC_]]

## Goals

Goals of this development stage:

- Verification of the service's conformity to SCIM RFCs.
- Technical writer can start working on the official documentation of the Nubus SCIM REST service
  - Including the documentation of non-conforming parts
- Performance tests show maximum read and write performance.

## Result

- In this MS the SCIM server does not provide access to UDM data.
  No reading from or writing to UDM happens at all.
- SCIM reads and writes go directly to the SCIM DB.
- Dependency inspection of the SCIM service's availability and performance on UDM do not apply yet.
- The SCIM server issues events to the Provisioning system when it changes SCIM objects.
  - The Provisioning system receives and distributes events of type `{"realm": "scim", "topic": "user"}` and `{"realm": "scim", "topic": "group"}`.
- Performance tests show maximum read and write performance of SCIM server and database backend.
  - Read performance is at its maximum. This should not change in MS2 or MS3.
  - Write performance is at its maximum.
    - Serialized creates, moves and deletes are significantly faster than UDM.
    - Serialized updates of attributes have comparable performance.
    - Serialized updates of group membership are significantly faster.
    - Parallel changes of all kinds are significantly faster than UDM.
  - Delay between SCIM and UDM databases does not apply yet.

## Components overview

![Components overview (milestone 1)](images/components-ms1-old-overview.png "Components overview (milestone 1)")

## Sequence diagram: Reading from SCIM REST API

![Sequence diagram (milestone 1): Reading from SCIM REST API](images/sequence-ms23-scim-read.png "Sequence diagram (milestone 1): Reading from SCIM REST API")

## Sequence diagram: Writing to SCIM REST API

![Sequence diagram (milestone 1): Writing to SCIM REST API](images/sequence-ms1-old-scim-write.png "Sequence diagram (milestone 1): Writing to SCIM REST API")

## Authentication

- The SCIM REST API can be used without authenticating.
- The SCIM database's connection settings are read from the environment.
  Secrets (passwords, certificates etc.) are read from files whose paths are in environment variables.

## Authorization

- Restrictions defined in the SCIM RFCs apply (e.g., the `id` field is read-only).
- No further authorisation happens.
  All operations on all objects and attributes are allowed, unless forbidden by the SCIM specification.

## Navigation

- Previous chapter: [Nubus SCIM service Architecture](Nubus-SCIM-service-architecture.md)
- Next chapter: [Milestone 2: Synchronous writes to UDM, reads from SQL](milestone2.md)
