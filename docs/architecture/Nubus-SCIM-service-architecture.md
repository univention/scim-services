# Nubus SCIM service architecture

[[_TOC_]]

## Introduction / Business Case

The System for Cross-domain Identity Management (SCIM) is a standard for exchanging user identity information.
The specification is split up into multiple RFCs.
Links can be found in the [README](../README.md).

Nubus already has an API for that purpose: The Univention Directory Manager (UDM).
UDM is not a standard.
Thus, Univention and customers are forced to create and maintain dedicated integrations.

Nubus' SCIM service offers access to the data in Nubus' UDM database.
That allows Univention and customers to reduce development and maintenance effort,
when they use the same standardized interface that other IAM providers like Okta, Entra ID, etc. offer.

TODO: Input from PM here please.

## Use cases

TODO: Input from PM here please.

## Requirements

A [Scenario description](https://git.knut.univention.de/univention/requirements-management/-/issues/297) exists in the
Requirements Management Board.
Use cases and requirements are missing.

The following requirements were extracted from an email (2025-02-19).
The following list is my understanding of the email.
It has not been vetted by PM yet (2025-02-21):

- The SCIM service MUST function in environments with over 100,000 users.
  - Clarification needed: What does "function" mean?
- The SCIM service MUST handle parallel requests to the same object.
  - Clarification needed: Handle how?
- The SCIM service MUST safely handle asynchronous changes to data in the UDM backend.
  E.g., when the AD connector changes data.
- Asynchronous processes like connectors and consumers MUST handle situations where the objects referenced by an event
  changed or were deleted in the database.
- Under load, the SCIM service MUST behave consistently towards other services.
  - Clarification needed: What does "behave consistently towards other services" mean?
- The UDM <-> SCIM attribute mapping does not need to be configurable.
- Performance: see section [Performance](#Performance)
- Observability: see section [Observability](#Observability)
- Authentication: see section [Authentication](#Authentication)
- Authorization: see section [Authorization](#Authorization)
- Brute-force prevention and rate limiting SHOULD be implemented in a later development iteration.
- The SCIM service initially only needs to support the management of user and group objects.
- The SCIM schema and the SCIM<->UDM mapping are configurable.
  - SCIM schema extensions are supported.
  - UDM extended attributes are supported.
  - A mapping will not be generated automatically, but can be configured.

### Authentication

The SCIM RFCs purposefully do not specify authentication or authorization.
It is left up to the SCIM service provider to implement those according to their needs,
e.g. ensuring that only authorized SCIM clients have access.
The specification recommends using industry-standard authentication protocols like OAuth 2.0.

From the PM email (2025-02-19):

- The SCIM service MUST NOT be used unauthenticated.
- The SCIM service MUST support OAuth authentication.

What other SCIM providers do:

- Entra ID requires an OAuth token
  (see [Microsoft SCIM docs](https://learn.microsoft.com/de-de/entra/identity/app-provisioning/use-scim-to-provision-users-and-groups)).
- Okta recommends using the OAuth 2.0 authorization, but also supports basic auth and header token auth options
  (see [SCIM technical questions](https://developer.okta.com/docs/concepts/scim/faqs/)).
- Slack requires an OAuth token (see [Slack - Accessing the SCIM API](https://api.slack.com/admins/scim#access)).

---

We will implement this in the following way:

- We require a Bearer token in an HTTP `Authorization` header.
- We verify the signature of the token against a certificate provided by the IdP (see below).
  - The certificate to verify the OAuth tokens is downloaded from Keycloak every time the service starts
    (see https://www.keycloak.org/securing-apps/oidc-layers for endpoints).
  - The IdP's configuration can be found at `https://<idp-url>/realms/{realm-name}/.well-known/openid-configuration`.
  - The public keys for validating the token should be fetched from the URL defined in the `jwks_uri` field of the IdP's configuration.
- We trust the IdP-signed token content.
- The user in the token is the SCIM _client_ / _tenant_.

### Authorization

Like with authentication, SCIM does not define any authorization mechanism.

From the PM email (2025-02-19):

- No use cases are known atm.
  In later development iterations fine-granular authorizations, using the Guardian, SHOULD be possible.
  - Clients SHOULD be able to enquire what attributes they are allowed to change.
    - @dtroeder: Please note that [RFC 7644, section 4, "Service Provider Configuration Endpoints"](https://datatracker.ietf.org/doc/html/rfc7644#section-4)
      "defines three endpoints to facilitate discovery of SCIM service provider features and schema."
      When the visibility or writability of an attribute is limited for a connecting user,
      those endpoints can be used to communicate that.
  - A Nubus operator SHOULD be able to configure which UDM attributes a SCIM service account can read and write.
    - Clarification needed: Shouldn't SCIM and UDM adhere to the same RAM rules?

---

We will implement this in the following way:

- MS1: The client/user in the token must exist as a `users/ldap` or `users/user` object in UDM and
  must be member of a certain `groups/group` object in UDM.
  - When a request comes in it must be authenticated.
    Thus, we retrieve the mentioned group from UDM or a cache.
  - We cache the group data for a _configurable_ number of seconds.
  - If the client/user is member of that group, then it is permitted access, otherwise denied.
  - We do not support nested groups.
  - _Update_: We may configure Keycloak to do the authz, and just check the token.
    The description in this section will be updated when it's clear if that approach works.
    The work is done in [issue #1151](https://git.knut.univention.de/univention/dev/internal/team-nubus/-/issues/1151).
- MS2: The client/user in the token must exist as a user object in the SCIM (SQL) DB and
  must be member of a certain group object in the SCIM DB.
  - When a request comes in it must be authenticated.
    Thus, we retrieve the mentioned group from the SCIM DB.
  - If the client/user is member of that group, then it is permitted access, otherwise denied.
  - We do not support nested groups.

### Performance

From the PM email (2025-02-19):

- The SCIM service MUST have "acceptable response times".
  - Clarification needed: Need numbers / KPIs. "Acceptable" is not verifiable.
  - TODO: Investigate what other offerings (Entra ID, Okta, …) declare.
- The SCIM service SHOULD be able to "initialize" the user database with 100,000 users in less than a week.
  Better would be in one day.
  Parallelization of client requests can be expected.
- The SCIM service SHOULD achieve five or more updates of an existing user object per second.
  Parallelization of client requests can be expected.

### Observability

#### Logging

From the PM email (2025-02-19):

- The SCIM service, the UDM REST API and the Provisioning services SHOULD log the same unique object and request IDs.
- The SCIM service error messages SHOULD contain information and hints that help operators to handle the problems.
- The SCIM service SHOULD log in a format that can be processed by 3rd party software like log collectors.
  - Univention has released multiple ADRs regarding logging. They must be followed:
    - [ADR dev/0005 Log Levels](https://git.knut.univention.de/univention/decision-records/-/blob/main/dev/0005-log-levels.md) defines what log levels exist and how to use them.
    - [ADR dev/0006 Log Format](https://git.knut.univention.de/univention/decision-records/-/blob/main/dev/0006-log-format.md) defines the content and format of log messages.
    - [ADR dev/0007 Log Messages](https://git.knut.univention.de/univention/decision-records/-/blob/main/dev/0007-log-messages.md) defines the content and metadata of log messages.
    - [ADR dev/0008 Structured Logging](https://git.knut.univention.de/univention/decision-records/-/blob/main/dev/0008-structured-logging.md) defines the use of structured logging.
  - The [liblancelog](https://git.knut.univention.de/univention/dev/libraries/lancelog) library MUST be used to
    configure logging.

- All SCIM HTTP requests have a unique ID.
  - This "request ID" can be passed in by SCIM HTTP clients in the `X-Request-ID` HTTP header.
  - If not received from the client, the SCIM REST server creates a UUID.
  - Univention has in the past used the [asgi-correlation-id](https://github.com/snok/asgi-correlation-id) Python library for this purpose.
- All SCIM HTTP responses contain the request ID from the previous bullet point in the `X-Request-ID` HTTP header.
All log lines MUST:
  - … be _prefixed_ with the request ID (see bullet points above).
    The UUID can be shortened to 10 characters.
  - … contain the `id` field of the object that is being worked on, in the context variables.
  - … contain the `externalId` field, if it is not empty, in the context variables.
  - … contain the `univentionObjectIdentifier` field, if it is not empty, in the context variables.
  - … contain the `dn` field, if `univentionObjectIdentifier` is empty and `dn` is not, in the context variables.

#### Metrics

- The SCIM server collects metrics and makes them available to operators.
  - Non-exhaustive list of metrics:
    - Number of requests, separate _counter_ (label) for each HTTP method (`GET`, `POST`, `PATCH`, `PUT`, `DELETE`) and resource (`User`, `Group`).
    - Duration of requests, separate _histogram_ (label) for each HTTP method and resource.
    - Number of errors on the SCIM REST interface, separate _counter_ (label) for each HTTP method and resource.
    - Number of requests to the UDM REST API, separate _counter_ (label) for each HTTP method and resource.
    - Number of errors talking to the UDM REST API, separate _counter_ (label) for each HTTP method and resource.
    - Duration of requests to the UDM REST API, separate _histogram_ (label) for each HTTP method and resource.
    - Number of synchronization requests by the UDM2SCIM consumer to the SCIM REST API, separate _counter_ (label) for each HTTP method and resource.
    - Number of synchronization errors by the UDM2SCIM consumer.
    - Duration of synchronization requests by the UDM2SCIM consumer to the SCIM REST API, separate _histogram_ (label) for each HTTP method and resource.
    - Number of errors by the Model->Mapping component, separate _counters_ (labels) for mapping from SCIM to UDM and UDM to SCIM, and for each resource.
    - Number of objects in the SCIM database, separate _counters_ (labels) for each resource (`User`, `Group`).
  - The metrics are exposed as a Prometheus endpoint.
  - _TODO:_ Clarify if authentication is required for scraping.
- The SCIM server provides a healthcheck endpoint for the Kubernetes API.

#### Tracing

From the PM email (2025-02-19):

- No requirements from PM.
  @dtroeder: But we should evaluate instrumentation using OpenTelemetry.
  That would support implementing the goal the unique object and request IDs in logs have: Traceability.
- @dtroeder: Having traces massively reduces debug time.
  Finding out where a request fails in a call chain, or which component is slowing the system down, becomes very easy.
  This leads to reduced development and support efforts.

## Identifiers

Identifiers for objects exist in LDAP, UDM, and SCIM.
This section describes their purposes and how to map one to the other.

### SCIM

In SCIM the `id` and `externalId` fields are defined in [RFC7643 section 3.1. Common Attributes](https://datatracker.ietf.org/doc/html/rfc7643#section-3.1).
Important characteristics:

- `id`
  - Every representation of a SCIM resource MUST include a non-empty `id` value.
  - The value MUST be unique across the SCIM service provider's entire set of resources.
  - The value of the `id` attribute is always issued by the service provider and MUST NOT be specified by the client.
  - The string `bulkId` is a reserved keyword and MUST NOT be used within any unique identifier value.
  - The attribute characteristics are `caseExact=true`, `mutability=readOnly`, and `returned=always`.
    The type is `String`, without further limitations.
- `externalId`
  - This attribute is OPTIONAL. Each resource MAY include a non-empty `externalId` value.
  - The value of the `externalId` attribute is always issued by the provisioning client and MUST NOT be specified by the service provider.
  - While the server does not enforce uniqueness, it is assumed that the value's uniqueness is controlled by the client setting the value.
  - The service provider MUST always interpret the `externalId` as scoped to the provisioning domain.
  - The attribute characteristics are `caseExact=true` and `mutability=readWrite`.
    The type is `String`, without further limitations.

---

We will implement this in the following way:

- `id`
  - We will map this attribute to the UDM property `univentionObjectIdentifier`.
    - This mapping is NOT configurable.
  - The format will be limited to a UUID v4 string (e.g., `9c5b94b1-35ad-49bb-b118-8e8fc24abf80`).
- `externalId`
  - The UDM property for the mapping is configurable.
    - See section _Scoping of `externalId`_ for an additional configuration requirement.
    - The customer "BaWü" wants us to map `externalId` to the UDM property `dapExternalIdentifier`.
  - The format will be a `String` without further limitations.

#### Scoping of `externalId`

When the RFC says that the `externalId` MUST be scoped to the provisioning domain, it means that one ID is stored _per client/tenant_.

This feature allows multiple clients or tenants to store an ID from their database in the SCIM service's object,
without overwriting the values in `externalId` created by other clients.

This is useful when multiple IdPs / upstream systems work with the SCIM service.

[RFC7643 section 9.3 "Privacy"](https://datatracker.ietf.org/doc/html/rfc7643#section-9.3) mentions privacy considerations:
In the case of `externalId`, if multiple values are supported,
use access control to restrict access to the client domain that assigned the `externalId` value.

[RFC7644 section 6.1 "Associating Clients to Tenants"](https://datatracker.ietf.org/doc/html/rfc7644#section-6.1) says:
The service provider MAY use one of the authentication mechanisms discussed in [Section 2](https://datatracker.ietf.org/doc/html/rfc7644#section-2)
to determine the identity of the client and thus infer the associated Tenant.
For implementations where a client is associated with more than one Tenant,
the service provider MAY use one of the three methods below for explicit specification of the Tenant.
If any of these methods of allowing the client to explicitly specify the Tenant are employed,
the service provider should ensure that access controls are in place to prevent or allow cross-tenant use cases.
In all of these methods, the `{tenant_id}` is a unique identifier for the Tenant as defined by the service provider.

- A URL prefix: `https://www.example.com/Tenants/{tenant_id}/v2/Users`.
- A sub-domain: `https://{tenant_id}.example.com/v2/Groups`.
- An HTTP header: The service provider may recognize a `{tenant_id}` provided by the client in an HTTP header
  as the indicator of the desired target Tenant.

---

We will implement this in the following way:

- We will not allow to explicitly specify the tenant.
- We will not support multiple clients per tenant. Every client is a tenant.
- The `externalId` will be scoped to the client.
- The client's ID will be extracted from the OAuth token.
- Only one `externalId` value will be mapped to UDM/LDAP.
  - To configure the mapping of `externalId` to UDM/LDAP, one scope/client ID and one UDM property name MUST be supplied.

## Relation with UDM

The SCIM service for Nubus is designed to work independently of UDM, and UDM to work independently of SCIM.
The availability and performance of one service does not affect the availability or performance of the other service.

The system is deliberately designed not to have (or require) a single source of truth.
This setup allows us to incrementally replace UDM clients with SCIM clients and eventually completely deprecate UDM.

The above is not a requirement of the current customer project or by product management.
It is part of the software architect's long-term development strategy to modernize Nubus.

A [bijective](https://en.wikipedia.org/wiki/Bijection) mapping is imperative to achieve data consistency between the two data models.
It ensures that each UDM property is synchronized with exactly one SCIM attribute and vice versa.
The bidirectional synchronization depends on the bijective mapping to prevent an infinite loop.
The mapping can be found in the [Mapping UDM <-> SCIM v2](../udm-scim-mapping.md) document.

The bijective function does not need to be complete.
It is allowed for attributes not to be synchronized.
But if they are synchronized, a one-to-one correspondence is mandatory.

## Database choice

The SCIM specification is database agnostic, as an API should be.
We must strive to not leak implementation details, like database-specific references, to API clients.
The mistakes that were made in the design of the UDM API,
tying all applications strongly to a specific implementation,
must not be repeated.

In SCIM, references (e.g., group membership) contain relational data.
From UCS@school and the Guardian we know the performance problems relational data causes with an LDAP database.

The namespacing in SCIM schemas allows the database schema to be normalized.
Relational databases allow applications to move the effort of joining the normalized data to the database server.

Thus, the SCIM service should be implemented using a relational database.
The integration of a different data model with the existing one (UDM) is part of the modernization of Nubus.
See [New architecture for UCS@school](https://dtroeder.gitpages.knut.univention.de/future-of-nubus/ucsschool-software-architecture.html#new-architecture-for-ucs-school).

The Command and Query Responsibility Segregation (CQRS) pattern allows us to optimize for different use cases and performance requirements
(see the respective section in the [Milestone 2](milestone2.md) page).

Relational Database Management System (RDBMS) are commodity software.
A few Nubus components already require an SQL database.
In UCS, Debian's Univention-supported PostgreSQL is used.
In Nubus for Kubernetes customers are expected to provide their own database (cluster).

## Handling passwords and password hashes

`password` is a default user attribute in SCIM.
If a value is sent, it needs to be passed on to UDM.

If no value is set when creating a user, this is also passed on to UDM.
At the moment UDM does not allow the creation of users with empty passwords.

UDM will be adapted to accept an empty password.
It will then generate and store a random one.

Until that's implemented, when no password is given by the SCIM client, the workaround is to generate a random one.

The SCIM service itself does not need a password or password hash for authentication,
because OAuth is used and the authentication is done by the IdP.
The password or hash can never be read through SCIM.
So, there is no need to store the password or a password hash in the SCIM DB (MS2+).

## Configuration

- All configuration including secrets must be loaded and validated at startup.
- Default values are _not_ specified in the source code, but instead are the responsibility of the deployment code
  (Helm / Docker Compose).
- At startup, the service should validate as much settings as possible, so it can fail early.
- Configuration is not reloaded at runtime.
  Instead, the process must be restarted for any environment variable or secret file changes to take effect.
- In Python, all configuration is loaded by [Pydantic Settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)
  objects.
- The configuration is logged at service start.
  Secrets are masked in the output.

## Secrets handling

The SCIM service's components read all sensitive data they need for operations,
so-called "secrets" (passwords, certificates etc.),
from files whose paths are in environment variables.

If for example the SCIM 2 UDM Consumer wants to access the UDM REST API,
then it can find its hostname (FQDN) and the account (an LDAP DN) in the environment,
e.g. in `UDM_HOST` or `UDM_URI` and `UDM_USER_DN`.

The password however is stored in a file (e.g., `/run/secrets/udm_password`) inside the container,
and an environment variable contains that files path, e.g. `UDM_PASSWORD_FILE=/run/secrets/udm_password`.
The path must not be hard coded in Python.

There might be data, like for example an SSL certificate, that is better stored in a file than an environment variable.
Their paths must also be read from the environment, and not be hard coded in Python.

The names of environment variables for file paths should end in `_FILE`.
That is a convention used by popular container images.

- Official documentation about secrets handling for [Docker Compose](https://docs.docker.com/compose/how-tos/use-secrets/).
- Official documentation about secrets handling for [Kubernetes](https://kubernetes.io/docs/concepts/configuration/secret/).

## Logging

Logging MUST follow the rules laid out in the following ADRs:

- [ADR 0004 Logging Topology](https://git.knut.univention.de/univention/decision-records/-/blob/main/dev/0004-logging-topology.md)
- [ADR 0005 Log levels](https://git.knut.univention.de/univention/decision-records/-/blob/main/dev/0005-log-levels.md)
- [ADR 0006 Log format](https://git.knut.univention.de/univention/decision-records/-/blob/main/dev/0006-log-format.md)
- [ADR 0007 Log messages](https://git.knut.univention.de/univention/decision-records/-/blob/main/dev/0007-log-messages.md)
- [ADR 0008 Structured logging](https://git.knut.univention.de/univention/decision-records/-/blob/main/dev/0008-structured-logging.md)

To implement a compatible logging setup, use the [Lancelog](https://git.knut.univention.de/univention/dev/libraries/lancelog) library.

Structured logging is MANDATORY.
It is not only about the output format.
For your logs to be well parsable by humans and machines, _the event and the data must be separately recognizable_.

Basically, log the event in the text message and data as separate arguments:

```diff
- logger.info(f"Created {num} users in {ou} using {request.method}.")
+ logger.info("Created users.", amount=num, ou=ou, method=request.method)
```

See the README of Lancelog for more syntactic sugar.

## Deliverables

The SCIM service will be provided to Nubus for Kubernetes and UCS customers.
Thus, it must be packaged for use by the Helm package manager and the Univention App Center.

Details change from milestone to milestone.

## Hexagonal architecture

Components of the service are structured using ["Hexagonal architecture"](https://en.wikipedia.org/wiki/Hexagonal_architecture_(software))
(also known as "Ports and Adapters architecture"),
which is a subset of the "clean architecture" proposed by Robert C. Martin.

This architecture promotes loose coupling of components,
a strict separation of application and environment,
and makes components easily exchangeable.

The latter comes in handy during development, e.g., when the data backends change from milestone to milestone,
or when we decide to change the method how UDM<->SCIM mappings are implemented.

But it can also provide fall-backs at operation or delivery time for problematic situations like, e.g.,
when there is not enough time to fix a case of inconsistency in an asynchronous call chain,
we can swap the asynchronous implementation with a synchronous one that may be slower but safer.

Requisites for Hexagonal architecture are [dependency inversion](https://en.wikipedia.org/wiki/Dependency_inversion_principle)
and [inversion of control](https://en.wikipedia.org/wiki/Inversion_of_control).
Using dependency injection helps implement it.

### Dependency injection

To further promote the loose coupling of components, [dependency injection](https://en.wikipedia.org/wiki/Dependency_injection)
is used to separate the construction and the use of objects.

It is also helpful when running code in different configurations or environments,  e.g. on different platforms.

Additionally, this helps when writing tests, because mocking and patching are not needed.
No patching reduces the effort for the long term maintenance of tests.

Three Python libraries should be evaluated:

- [port-loader](https://git.knut.univention.de/univention/components/port-loader) was developed for and is used by the
  [Guardian](https://git.knut.univention.de/univention/components/authorization-engine/guardian) to help implement its
  hexagonal architecture.
  It supports loading dependencies from [Python Entry Points](https://setuptools.pypa.io/en/latest/userguide/entry_point.html)
  and offers per-port configuration classes.
  The Guardian is in production and the "port-loader" has proven useful during production and maintenance.
  Its API is a bit clunky, but not that bad.
- [pytheca](https://github.com/SamuelYaron/pytheca) is a new project by the main developer of the "port-loader".
  It is born from the wish for a cleaner API.
  It does not yet support the same features, but is expected to do so soon;
  at least those, that are interesting for this project.
- [Dependency Injector](https://python-dependency-injector.ets-labs.org/) is a mature, production-ready, well-tested,
  documented, and supported dependency injection framework with lots of contributors and users.
  It supports everything the "port-loader" does and much more.
  It's so powerful, it is a bit overwhelming.
  But the good examples and documentation help to find what you need.

_Update:_ We have decided to on the DI library.
We have started using the [Python Dependency Injector](https://python-dependency-injector.ets-labs.org/).

### Example code

An example application implementing Hexagonal architecture,
and using the _Dependency Injector_ framework can be found at:
https://git.knut.univention.de/univention/dev/docs/dev-guidelines/-/tree/main/examples/dependency-injector

## Architecture tests

To ensure the implementation adheres to the [intended architecture](#hexagonal-architecture),
tests have been written (currently in [scim-server/tests/test_architecture.py](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/-/blob/main/scim-server/tests/test_architecture.py)).

The tests use the [PyTestArch](https://zyskarch.github.io/pytestarch/latest/) library.
The library builds a graph from the imports of all Python modules,
and then allows to validate rules about those imports.

Tested is for example, that the core business logic doesn't import code from any place outside the business layer.
That is the central idea of the Hexagonal and Clean architecture.

Another test verifies that adapters (of ports) don't import each other.
That is not strictly necessary, but improves decoupling and thus independent development.
If common code exists in adapters, it should be refactored into a separate module.
That module can be imported by those adapters.

## Development milestones

The development of the SCIM service is done in three milestones.
In each MS the way data is read and written changes.
Please continue with Milestone 1.

- [Milestone 1: Minimal viable product | Synchronous adapter in front of UDM](milestone1.md)
- ([Archived: _Deprecated_ Milestone 1: Standalone SCIM server](milestone1-old.md))
- [Milestone 2: Synchronous writes to UDM, reads from SQL](milestone2.md)
- [Milestone 2.1: Add metrics, provisioning](milestone2.1.md)
- [Milestone 3: Asynchronous writes to UDM](milestone3.md)
