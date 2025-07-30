# Scim server

## Installation

```bash
cd scim-server
uv pip install --requirements pyproject.toml
```

or for dev dependencies also:

```bash
uv pip install --all-extras
```

## Usage

### Local development

```bash
AUTH_ENABLED=false uv run uvicorn --reload src.univention.scim.server.main:app
```

### With Nubus backend

- Add `http://127.0.0.1:8000/docs/oauth2-redirect` to the `Valid redirect URIs` of the keycloak client
- Add `http://127.0.0.1:8000` to the `Web origins` of the keycloak client

```bash
./run_with_nubus.sh
```

## Testing

```bash
uv run pytest
```
