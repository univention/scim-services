# Scim

## Architecture

- [Nubus SCIM service architecture](architecture/Nubus-SCIM-service-architecture.md)
  - [Milestone 1: Minimal viable product | Synchronous adapter in front of UDM](architecture/milestone1.md)
  - ([Archived: _Deprecated_ Milestone 1: Standalone SCIM server](architecture/milestone1-old.md))
  - [Milestone 2: Synchronous writes to UDM, reads from SQL](architecture/milestone2.md)
  - [Milestone 2.1: Add metrics, provisioning](architecture/milestone2.1.md)
  - [Milestone 3: Asynchronous writes to UDM](architecture/milestone3.md)
- [UDM <-> SCIM mapping](udm-scim-mapping.md)

## Existing Python SCIM software

- [Copy & pastable CLI instructions](python-scim-server-test.md) for a quick test of the open source Python [scim2-server](https://github.com/python-scim/scim2-server) project

## RFCs

Relevant RFCs:

- Overview, definitions, and concepts: [RFC7642 - System for Cross-domain Identity Management: Definitions, Overview, Concepts, and Requirements](https://datatracker.ietf.org/doc/html/rfc7642).
- Data schema: [RFC7643 - System for Cross-domain Identity Management: Core Schema](https://datatracker.ietf.org/doc/html/rfc7643).
- REST interface: [RFC7644 - System for Cross-domain Identity Management: Protocol](https://datatracker.ietf.org/doc/html/rfc7644).

Unrelated RFCs about SCIM:

- Provisioning interface: [SCIM Event Notification (draft-hunt-scim-notify-00)](https://datatracker.ietf.org/doc/html/draft-hunt-scim-notify-00) (draft).
- User Self-Service interface: [SCIM Password Management Extension (draft-hunt-scim-password-mgmt-00)](https://datatracker.ietf.org/doc/draft-hunt-scim-password-mgmt/) (expired draft).
- Self-registration interface: [SCIM Profile For Enhancing Just-In-Time Provisioning (draft-wahl-scim-jit-profile-002)](https://datatracker.ietf.org/doc/draft-wahl-scim-jit-profile/) (expired draft).
