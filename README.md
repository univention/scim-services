# SCIM services

---

[[_TOC_]]

## Introduction

The System for Cross-domain Identity Management (SCIM) is a standard for exchanging user identity information.

The specification is split up into multiple RFCs.
See [RFCs](#RFCs)

Nubus already has an API for the purpose of managing user identities: The Univention Directory Manager (UDM).
But, UDM is not a standard.
Thus, Univention and customers are forced to create and maintain dedicated integrations.

Nubus' SCIM service offers access to the data in Nubus' UDM database.
That allows Univention and customers to reduce development and maintenance effort,
when they use the same standardized interface that other IAM providers like Okta, Entra ID, etc. offer.

### RFCs

- Overview, definitions, and concepts: [RFC7642 - System for Cross-domain Identity Management: Definitions, Overview, Concepts, and Requirements](https://datatracker.ietf.org/doc/html/rfc7642).
- Data schema: [RFC7643 - System for Cross-domain Identity Management: Core Schema](https://datatracker.ietf.org/doc/html/rfc7643).
- REST interface: [RFC7644 - System for Cross-domain Identity Management: Protocol](https://datatracker.ietf.org/doc/html/rfc7644).

## Installation /  Deployment

### Nubus for Kubernetes

TODO

### UCS

TODO

## Configuration

### Nubus for Kubernetes

TODO

### UCS

TODO

## Documentation

- Development documentation is in the [docs](docs) directory.
- Public documentation: TODO

## Development

- This project uses [pre-commit](https://pre-commit.com/) for managing and maintaining pre-commit hooks.
- This project uses [uv](https://docs.astral.sh/uv/) as Python package and project manager.
  - This repository is a _uv workspace_, with [scim-server](scim-server),
    [scim-udm-transformer-lib](scim-udm-transformer-lib)
    as _workspace members_.
- ...

### Scim server

**Move into server folder:**

```bash
cd scim-server
```

**Install dependencies:**

```bash
uv pip install --requirements pyproject.toml
```

or for dev dependencies also:

```bash
uv pip install --all-extras
```

**Run locally in dev mode:**

```bash
AUTH_ENABLED=false uv run uvicorn --reload src.univention.scim.server.main:app
```

**Run locally but use nubus deployment as backend:**
- Add `http://127.0.0.1:8000/docs/oauth2-redirect` to the `Valid redirect URIs` of the keycloak client
- Add `http://127.0.0.1:8000` to the `Web origins` of the keycloak client

```bash
./run_with_nubus.sh
```

**Run tests:**

```bash
uv run pytest
```

#### Tests

- To start unit tests:  TODO
- To start integration tests:  TODO
- To start end-to-end tests:  TODO

### SCIM client

#### Tilt setup

To develop the scim-client helm chart and container image, you can run it in Tilt.

You can deploy the dependencies via the normal dev-env:
`tilt up keycloak ldap-server ldap-notifier udm-rest-api stack-data-ums provisioning provisioning-udm-listener`

There is one step of "manual" configuration necessary.
We need to register the Nubus Provisioning subscription for the SCIM client.
For this purpose the scim-client helm chart creates a secret named `scim-client-provisioning-subscription`
this Secret contains an embedded json file defines the subscription.
We can use the `register-clients` job of the `provisioning` helm chart
to create the subscription in the Provisioning API for us.

All we need to do is configure the additional secret in the `custom-values.yaml`
of the `provisioning` chart.

`helm-values/values-provisioning.yaml`

```json
registerConsumers:
  createUsers:
    scimClient:
      existingSecret:
        name: scim-client-provisioning
        keyMapping:
          password: "registration"
```

### Helm unittests

To run the helm unittests, execute the following command in the project root:
`docker compose -f helm/docker-compose.yaml run --rm -it test`
