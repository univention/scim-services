# Milestone 2.1: Add metrics, provisioning

[[_TOC_]]

This stage introduces new features and qualities without changing the interaction between SCIM and UDM.

- The SCIM service generates metrics.
- The SCIM service generates Provisioning events.
- ...

## Goals

Goals of this development stage:

- Add new features and qualities to the SCIM service without changing the interaction between SCIM and UDM.
- Operators of the SCIM service can collect metrics that help them understand the systems state and performance.
- Partners and developers can create Provisioning Consumers that subscribe to IAM events with SCIM object payloads.
- ...

## Result

- The SCIM server collects metrics and makes them available to operators.
  - See [section "Metrics" of the "Nubus SCIM service architecture" page](https://git.knut.univention.de/univention/dev/projects/scim/scim-dev-docs/-/blob/main/architecture/Nubus-SCIM-service-architecture.md#metrics)
    for a list of metrics to collect and how to expose them.
  - The SCIM server provides a healthcheck endpoint for the Kubernetes API.
  - The documentation explains how to retrieve the metrics.
- The SCIM server issues events to the Provisioning system.
  - When the SCIM server changes SCIM objects, the Provisioning system receives and distributes events of type
    `{"realm": "scim", "topic": "user"}` and `{"realm": "scim", "topic": "group"}`.
    - Events contain an attribute that can be used to determine the order of changes.
      The value is a monotonic growing integer set by the SCIM database.
      This can be used to fix the order of events in a queue, in case it is wrong because of asynchronicity.
      - Alternatively, or additionally, the `modifyTimestamp` of the corresponding call to the UDM REST API can be used.
  - Errors encountered by the UDM 2 SCIM Consumer that were previously only logged,
    are now additionally sent to the Provisioning with `{"realm": "sync-error", "topic": "udm2scim"}`.
    - The payload is a SCIM error JSON object with schema `urn:ietf:params:scim:api:messages:2.0:Error`
      (see [RFC 7644 section 3.12](https://datatracker.ietf.org/doc/html/rfc7644#section-3.12)).
  - The documentation mentions the new Provisioning event type and links to the general Nubus Provisioning documentation.
    - The general Nubus Provisioning documentation mentions that besides the `udm` realm,
      there are also the `scim` and `sync-error` realms.

## Components overview

TODO

## Sequence diagram: TODO

TODO

## Deliverables

The SCIM service will be provided to Nubus for Kubernetes and UCS customers.
Thus, from MS2 on, additionally to the Helm package manager, it must be packaged for use by the Univention App Center.

- The SCIM server Helm chart shouldn't be integrated with the Nubus umbrella chart.
- The SCIM server Helm chart is released in the `nubus` (production) branch on `artifacts.software-univention.de`.
- The SCIM server UCS App Center app is only released in the test App Center, not the production App Center.

## Navigation

- Previous chapter: [Milestone 2: Synchronous writes to UDM, reads from SQL](milestone2.md)
- Next chapter: [Milestone 3: Asynchronous writes to UDM](milestone3.md)
