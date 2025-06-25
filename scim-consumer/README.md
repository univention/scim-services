# SCIM Cunsumer

## Running tests local

The tests running agains the SCIM server from

```bash
docker compose --profile develop up --build --remove-orphans -d

docker compose --profile develop run --rm --build --remove-orphans test
# or
pytest -v -s ./

docker compose --profile develop down --volumes
```

To run the tests against the Univention SCIM server

```bash
docker compose --profile integration up -d --remove-orphans --build

docker compose --profile integration run --rm --build --remove-orphans test-integration
# or
UNIVENTION_SCIM_SERVER=true pytest -v -s ./

docker compose --profile integration down --volumes
```
