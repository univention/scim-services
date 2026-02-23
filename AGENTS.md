# AGENTS.md

This file provides guidance to AI agents when working with code in this repository.

## Repository overview

This is a `uv` workspace monorepo with three Python projects:

- **`scim-server`** — FastAPI-based SCIM v2 REST server. In Milestone 1 (current) it is a synchronous adapter: every SCIM request is translated into a UDM REST API call.
- **`scim-client`** — Experimental listener that subscribes to Nubus Provisioning API events and provisions changes to an external SCIM service provider.
- **`scim-udm-transformer-lib`** — Shared library for bidirectional UDM↔SCIM object transformation. Used by both `scim-server` and `scim-client`.

Only **Milestone 1** is implemented. Milestones 2, 2.1, and 3 (SQL database, async writes, provisioning events) are not yet built.

## Commands

### Install dependencies

```bash
# From repo root — installs all workspace members
uv sync --all-packages --all-extras
```

### Run scim-server locally

```bash
# No auth, auto-reload
cd scim-server
AUTH_ENABLED=false uv run uvicorn --reload src.univention.scim.server.main:app

# With a real Nubus backend
./run_with_nubus.sh
```

### Tests

The full test suite requires a running UDM REST API + LDAP server. The `docker-compose.yml` in `scim-server/tests/` spins these up.

```bash
# scim-server: full suite via Docker Compose (unit + integration)
cd scim-server/tests
docker compose run test

# scim-server: run pytest directly (requires UDM_URL, UDM_USERNAME, UDM_PASSWORD set)
cd scim-server
uv run pytest

# Single test file or test
uv run pytest tests/unit/test_user_mapping.py
uv run pytest tests/unit/test_user_mapping.py::test_my_function

# scim-client tests
cd scim-client/tests
docker compose run test

# SCIM2 compliance check
cd scim-server/tests
docker compose up -d ldap-server udm-rest-api scim-server
docker compose run scim2-tester
```

### Linting

```bash
# Ruff lint + format (run from repo root or any subproject)
uv run ruff check --fix --unsafe-fixes .
uv run ruff format .

# Mypy (strict mode, configured in root pyproject.toml)
uv run mypy scim-server/src
uv run mypy scim-udm-transformer-lib/src

# All pre-commit hooks at once
pre-commit run --all-files
```

Commits must follow [Conventional Commits](https://www.conventionalcommits.org/) — enforced by `pre-commit` on `commit-msg`.

## Architecture: scim-server

`scim-server` uses **Hexagonal (Ports & Adapters) architecture** with [Python Dependency Injector](https://python-dependency-injector.ets-labs.org/) for wiring.

### Layers

| Package | Role |
|---|---|
| `rest/` | **Driving adapter** — FastAPI route handlers; calls domain services |
| `domain/` | **Domain / business logic** — pure Python, no I/O, no framework imports |
| `domain/repo/udm/` | **Driven adapter** — UDM REST API backend; will be replaced in MS2 |
| `authn/` | Supporting adapter — OAuth/OIDC token validation via Keycloak JWKS |
| `authz/` | Supporting adapter — `aud`/`azp` claim verification |
| `model_service/` | Supporting — SCIM schema loading |
| `container.py` | DI wiring (`ApplicationContainer`) |
| `config.py` | `ApplicationSettings` (Pydantic Settings) + `DependencyInjectionSettings` |

### Strict layer constraints (enforced by `tests/unit/test_architecture.py`)

- **Domain must not import** `authn`, `authz`, `domain.repo.udm`, `model_service`, or `rest`. The business logic modules (`crud_scim`, `*_service*`, `repo/crud_*`, `rules/`) are technology-agnostic.
- **Adapters must not import each other**: `authn`, `authz`, and `domain.repo.udm` are mutually independent.
- `domain` **must** import `univention.scim.transformation` (the transformer lib).
- `rest` **must** import `domain`.

These rules are verified by [PyTestArch](https://zyskarch.github.io/pytestarch/latest/) — run `uv run pytest tests/unit/test_architecture.py` to check.

### Data flow (MS1)

```text
HTTP → rest/ → domain/*_service_impl.py → domain/repo/udm/crud_udm.py → UDM REST API → LDAP
```

`scim-udm-transformer-lib` handles all UDM↔SCIM object conversion. Port interfaces (`user_service.py`, `group_service.py`, `repo/crud_manager.py`) define the contracts; `*_impl.py` files contain the implementations.

### Dependency injection

Concrete implementations are configured via `DependencyInjectionSettings` (reads from `dependency-injection.env` or env vars). All class references are dotted Python paths. This allows swapping adapters (e.g., replacing the UDM repository with a SQL one) without changing business logic.

### Configuration

All settings use **Pydantic Settings** (`ApplicationSettings` in `config.py`). Key env vars:

| Env var | Description |
|---|---|
| `AUTH_ENABLED` | Enable/disable OAuth token validation (default: `true`) |
| `UDM_URL` | UDM REST API base URL |
| `UDM_USERNAME` / `UDM_PASSWORD` | UDM credentials |
| `API_PREFIX` | URL prefix, default `/scim/v2` |
| `PATCH_ENABLED` | Enable PATCH operations (default: `false`) |
| `EXTERNAL_ID_USER_MAPPING` | UDM property to map to SCIM `externalId` for users |
| `EXTERNAL_ID_GROUP_MAPPING` | UDM property to map to SCIM `externalId` for groups |

Secrets are always in files; the file path goes in an env var with a `_FILE` suffix (e.g., `UDM_PASSWORD_FILE`). Default values live in Helm/Docker Compose, not in Python source.

### Key identifier mapping

- SCIM `id` ↔ UDM `univentionObjectIdentifier` (UUID v4); this mapping is fixed and not configurable.
- SCIM `externalId` → configurable UDM property per OAuth client (identified by `azp` claim).

### UDM↔SCIM attribute mapping

The full mapping table is in `docs/udm-scim-mapping.md`. The `MS` column in those tables indicates in which milestone each mapping is/will be implemented. Only `MS=1` rows are currently implemented.

**Implemented (MS=1):**

| SCIM attribute | UDM property | Notes |
|---|---|---|
| `id` | `univentionObjectIdentifier` | Fixed, not configurable |
| `externalId` | *configurable* | Per OAuth client/tenant |
| `meta.*` | `createTimestamp`, `modifyTimestamp`, `objectType`, `uri`, ETag | |
| `userName` | `username` | |
| `name.givenName` | `firstname` | |
| `name.familyName` | `lastname` | |
| `name.formatted` | *(generated)* | Concatenated from firstname + lastname |
| `displayName` | `displayName` | |
| `emails` | `mailPrimaryAddress` (type=`mailbox`), `mailAlternativeAddress` (type=`alias`), `e-mail` (all other types) | Type-based routing |
| `password` | `password` | Write-only; never read back |
| `roles[type="guardian-direct"]` | `guardianRoles[]` | |
| `roles[type="guardian-indirect"]` | `guardianInheritedRoles[]` | Read-only |
| `Uni:User.description` | `description` | Univention User extension |
| `BaWü:User.primaryOrgUnit` | `primaryOrgUnit` | Customer extension (deprecated) |
| `BaWü:User.secondaryOrgUnits` | `secondaryOrgUnits` | Customer extension (deprecated) |
| Group `displayName` | `name` | |
| Group `members[type="User"]` | `users[]` | DNs resolved to UUIDs |
| Group `members[type="Group"]` | `nestedGroup[]` | DNs resolved to UUIDs |
| `Uni:Group.description` | `description` | Univention Group extension |
| `Uni:Group.memberRoles[type="guardian"]` | `guardianMemberRoles[]` | |

**Not yet implemented (MS=2 or later):**
- User `active` (`disabled`), `groups` (group memberships on user), `locale`, `PasswordRecoveryEmail`
- `addresses`, `phoneNumbers`, `title`, `userType`, `x509Certificates`, `employeeNumber`, and most remaining attributes

### SCIM schemas

The server serves the following schema URNs. The model classes live in `scim-server/src/univention/scim/server/models/` and `models/extensions/`.

| URN | Resource | Notes |
|---|---|---|
| `urn:ietf:params:scim:schemas:core:2.0:User` | User | RFC 7643 core |
| `urn:ietf:params:scim:schemas:extension:enterprise:2.0:User` | User | RFC 7643 enterprise extension |
| `urn:ietf:params:scim:schemas:extension:Univention:1.0:User` | User | Univention custom (description, passwordRecoveryEmail) |
| `urn:ietf:params:scim:schemas:extension:UniventionUser:2.0:User` | User | **Deprecated** — BaWü/DapUser customer extension; requires extended LDAP attributes |
| `urn:ietf:params:scim:schemas:core:2.0:Group` | Group | RFC 7643 core |
| `urn:ietf:params:scim:schemas:extension:Univention:1.0:Group` | Group | Univention custom (description, guardianMemberRoles) |

### Known limitations (MS1)

These are documented limitations relevant to development — not bugs to fix now:

- **`groups` not returned on User objects**: Computing group membership for every user is too expensive with the UDM backend.
- **PATCH disabled by default**: Set `PATCH_ENABLED=true` (env var) or `patch_enabled: true` (config) to enable. Tests set this via `pytest_env`.
- **No pagination**: Listing all resources fetches everything from UDM. The `count` parameter limits results but there is no cursor/offset pagination.
- **Performance of `GET /Groups/{id}`**: Resolving member UUIDs to DNs and back requires one UDM call per member.
- **Unknown group member on read**: Silently skipped (not mapped to SCIM).
- **Unknown group member on write**: Fails with HTTP 422.
- **No format validation**: Email, phone, address, and TLS certificate values are passed through without format checks.

### Logging

Use [lancelog](https://git.knut.univention.de/univention/dev/libraries/lancelog) to configure logging. Structured logging is mandatory — log event and data separately:

```python
# correct
logger.info("Created users.", amount=num, ou=ou, method=request.method)
# wrong
logger.info(f"Created {num} users in {ou} using {request.method}.")
```
