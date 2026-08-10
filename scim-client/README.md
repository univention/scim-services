# SCIM Client

## Purpose

The SCIM client is a component that connects to a SCIM-compliant service provider to provision users and groups. It acts as a bridge between the Nubus environment and other systems that support the SCIM standard.

## Status

**Experimental:** This component is currently experimental and intended for preliminary testing only. It is not yet recommended for production use.

## Limitations

- **Lack of Configurability:** The SCIM client currently has limited configuration options.
- **External ID:** The target SCIM server must be configured to handle the `externalId` attribute for mapping users and groups.

## Known Issues

There are no known issues at this time.

## How to Execute

To run the SCIM client, you need to deploy it using the provided Helm chart. See the installation guide for more details.

## How to Execute Tests

The tests running agains the SCIM server from

```bash
docker compose --profile develop up --build --remove-orphans -d

docker compose --profile develop run --rm --build --remove-orphans test
# or
pytest -v -s ./
# or without active venv
uv run pytest -v -s ./

docker compose --profile develop down --volumes
```

To run the tests against the Univention SCIM server

```bash
docker compose --profile test-integration up -d --remove-orphans --build

docker compose --profile test-integration run --rm --build --remove-orphans test-integration
# or
UNIVENTION_SCIM_SERVER=true pytest -v -s ./
# or without active venv
UNIVENTION_SCIM_SERVER=true uv run pytest -v -s ./

docker compose --profile test-integration down --volumes
```

## How to rum scim-client against a dedicated scim-server

### wire.com

Create a `.env` file for the configuration

```bash
export SCIM_SERVER_BASE_URL="https://prod-nginz-https.wire.com/scim/v2"
export PROVISIONING_API_BASE_URL="http://localhost:7777/"
export PROVISIONING_API_USERNAME="scim-client"
export PROVISIONING_API_PASSWORD="univention"
export PROVISIONING_API_ADMIN_USERNAME="admin"
export PROVISIONING_API_ADMIN_PASSWORD="provisioning"
export LOG_LEVEL="DEBUG"
export MAX_ACKNOWLEDGEMENT_RETRIES="10"
export UDM_BASE_URL="http://localhost:9979/udm/"
export UDM_USERNAME="cn=admin"
export UDM_PASSWORD="univention"
export LDAP_HOST="localhost"
export LDAP_BIND_DN="cn=admin,dc=univention-organization,dc=intranet"
export LDAP_BIND_PASSWORD="univention"
export EXTERNAL_ID_USER_MAPPING="univentionObjectIdentifier"
export EXTERNAL_ID_GROUP_MAPPING="univentionObjectIdentifier"
export MODULES='["users/user"]'
export KEYCLOAK_BASE_URL="http://localhost:5050"
export SCIM_AUTH_METHOD="bearer"
export SCIM_BEARER_TOKEN="<wire.com scim token>"
```

Create the subscription

```bash
cd scim-client
docker compose -f tests/docker-compose.yaml --profile develop up --build --remove-orphans -d
(source .env && uv run /bin/bash)
python3 -c "import tests.data.scim_helper as scim_helper; scim_helper.create_provisioning_subscription()"
```

Run the scim client and do your tests

```bash
(source .env && uv run scim-client)
```

```bash
(source .env && uv run /bin/bash)
udm --uri "http://localhost:9979/udm/" --username "cn=admin" --bindpwd "univention" users/user create --set username="jbu12345" --set lastname="Burgmeier" --set password="Test1234" --set e-mail="jbu@scim-client.unittests"
```

Cleanup

```bash
docker compose -f tests/docker-compose.yaml --profile develop down --volumes
```

## Interfaces

The SCIM client interacts with the following systems:

- **SCIM Service Provider:** The target server to which users and groups are provisioned.
- **Nubus Provisioning API:** Used to subscribe to user and group changes in the Nubus environment.
- **LDAP:** Used to retrieve user and group information.

## Dependencies

The SCIM client depends on the following services:

- A running Nubus for Kubernetes instance.
- A SCIM-compliant service provider.
- Nubus Provisioning API.
- LDAP server.

## Architecture

The SCIM client is a listener module that subscribes to object changes in the Univention Directory Manager (UDM). When a user or group is created, updated, or deleted in UDM, the Provisioning API sends a notification to the SCIM client. The SCIM client then transforms the UDM data into the SCIM format and sends it to the target SCIM service provider.

```mermaid
sequenceDiagram
    participant UDM
    participant Provisioning API
    participant SCIM Client
    participant SCIM Server

    UDM->>Provisioning API: User/Group Change
    Provisioning API->>SCIM Client: Notification
    SCIM Client->>LDAP: Get User/Group Data
    LDAP-->>SCIM Client: User/Group Data
    SCIM Client->>SCIM Client: Transform to SCIM
    SCIM Client->>SCIM Server: Provision User/Group
    SCIM Server-->>SCIM Client: Response
```
