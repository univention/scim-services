# SCIM Cunsumer

## Running tests local

The tests running agains the SCIM server from

```bash
docker compose up --build --remove-orphans -d

docker compose run --rm --build --remove-orphans test
# or
pytest -v -s ./

docker compose down --volumes
```

To run the tests against the Univention SCIM server

```bash
docker compose --file docker-compose-univention-scim.yaml up -d --remove-orphans --build

docker compose --file docker-compose-univention-scim.yaml run --rm --build --remove-orphans test
# or
UNIVENTION_SCIM_SERVER=true pytest -v -s ./

docker compose --file docker-compose-univention-scim.yaml down --volumes
```
