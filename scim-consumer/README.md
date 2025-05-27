# SCIM Cunsumer

## Running tests

```bash
docker compose --profile main up --remove-orphans -d

docker compose run --rm --build --remove-orphans test

docker compose --profile main down --volumes
```
