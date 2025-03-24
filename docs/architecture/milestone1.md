# Milestone 1: Minimal viable product | Synchronous adapter in front of UDM

[[_TOC_]]

## Goals

Goals of this development stage:

- Minimal viable product (MVP) that can be delivered to the customer.
  - The customer can test the functionality of the software and give early feedback.
  - Improved estimation of the effort for finalizing the whole project.
- Minimal set of features and attributes to reduce scope of MS.
- Verification of the service's conformity to SCIM RFCs - for the reduced feature and attribute set.
- Verification of the [UDM <-> SCIM mapping](../udm-scim-mapping.md).
  - No custom schema extensions.
  - The SCIM schema and the SCIM<->UDM mapping are not configurable.
  - The code to transform a UDM object to a SCIM object and vice versa is contained in a Python library.
    - The library can be used by the SCIM client project.
      That project allows to configure a synchronization between the LDAP (UDM) and a third party SCIM service.
- Technical writer can start working on the official documentation of the Nubus SCIM REST service.
  - Including the documentation of non-conforming parts.
- Performance tests show worse read and write performance than the UDM REST API.

## Result

- In this MS the SCIM server is an _adapter_ that converts the UDM REST API to the SCIM API.
- SCIM reads and writes go directly to the UDM REST API.
  No data is stored outside the LDAP server.
- The SCIM service's availability and performance are directly dependent to the UDM REST API's and the LDAP server's.
- The SCIM server does _not_ yet issue events to the Provisioning system.
  This feature is postponed to a later MS.
- Limited feature and attribute set:
  - Minimal mapping:
    - No complex attributes.
  - No custom schema extensions.
    - Only the default SCIMv2 schemas are used: `User`, `Group`, and the `Enterprise User` schema extension.
  - No custom resources (only `User` and `Group`).
    - `GET`, `POST`, `PUT`, and `PATCH` methods are supported for the `User` and `Group` endpoints.
    - `GET` supports only direct access to a single object and listing all objects.
      - Filtering, pagination, and sorting are not supported.
  - All requests using other resources, schemas, or attributes are rejected.
  - To prevent DOS situations at the UDM REST API and LDAP services,
    the LDAP database must not contain more than 10,000 users.
- Performance tests show worse read and write performance of SCIM server than the UDM REST API.
  - The additional requests necessary for resolving UUIDs to DNs have a massive impact on the read and write performance.
    This effect is especially problematic for groups with many members and users with many groups.
  - The use of a local, short-lived cache for DN <-> UUID mapping is advised.
    - Beware: DNs are mutable.
      Thus, there is a trade-off to be made between more cache-hits with a larger TTL and
      a higher likelihood of data corruption because of changed DNs.
      The Provisioning system can be used to listen for rename / move events and invalidate cache entries.
      But the effort is probably not worth the gain, because this MS is not final.
  - There is no delay between SCIM and UDM databases, as all requests are done synchronously.

## Components overview

![Components overview (milestone 1)](images/components-ms1-overview.png "Components overview (milestone 1)")

## Sequence diagram: Reading from SCIM REST API

![Sequence diagram (milestone 1): Reading from SCIM REST API](images/sequence-ms1-scim-read.png "Sequence diagram (milestone 1): Reading from SCIM REST API")

## Sequence diagram: Writing to SCIM REST API

![Sequence diagram (milestone 1): Writing to SCIM REST API](images/sequence-ms1-scim-write.png "Sequence diagram (milestone 1): Writing to SCIM REST API")

## Component details

![Component details (milestone 1)](images/components-ms1-details.png "Component details (milestone 1)")

## Authentication

- To use the SCIM REST API the client must send an OAuth token with the request.
  - Successful validation of the token is sufficient to gain access.
  - The content of the token does not matter and is ignored.
  - A certificate to verify the OAuth tokens is provided as a (bind mounted) file.
  - The path to the certificate file can be read from an environment variable.
- The SCIM REST server reads the UDM REST API's connection settings from the environment.
  - Secrets (passwords, certificates etc.) are read from files whose paths are in environment variables.
  - The LDAP account (the "bind dn") is configurable.
  - As BSI base security expects the password to be rotated, the `cn=admin` account shouldn't be used.
    Thus, a dedicated service account should be created.
  - For performance reasons, the account should profit from permissive LDAP ACLs.

## Authorization

- Restrictions defined in the SCIM RFCs apply (e.g., the `id` field is read-only).
- Restrictions in the UDM data model and business logic apply,
  when changes are forwarded _synchronously_ by the SCIM server.
  The SCIM server returns UDM errors to the SCIM client.
  - UDM REST API error messages are transformed to SCIM error messages that adhere to
    [RFC 7644 section 3.12](https://datatracker.ietf.org/doc/html/rfc7644#section-3.12).

## Deliverables

The MS1 version of the SCIM service will only be provided to a Nubus for Kubernetes customer.
Thus, it must only be packaged for use by the Helm package manager.

- The SCIM server Helm chart shouldn't be integrated with the Nubus umbrella chart.
- The SCIM server Helm chart is released in the `nubus-dev` (testing) branch on `artifacts.software-univention.de`.

## Navigation

- Previous chapter: [Nubus SCIM service Architecture](Nubus-SCIM-service-architecture.md)
- Next chapter: [Milestone 2: Synchronous writes to UDM, reads from SQL](milestone2.md)
- (Old chapter on MS1: [Milestone 1 OLD: Standalone SCIM server](milestone1-old.md))
